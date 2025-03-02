'''
Author:zhanghx(https://github.com/AdriftXCore)
date:2025-03-01 23:02:10
'''
import random

import cocotb
from cocotb.triggers import RisingEdge, Timer

async def generate_clock(dut, cycle, u, n):
    """Generate clock pulses."""
    if(n == 0):
        while True:
            dut.clk.value = 0
            await Timer(cycle/2, units=u)
            dut.clk.value = 1
            await Timer(cycle/2, units=u)
    else:
        for i in range(n):
            dut.clk.value = 0
            await Timer(cycle/2, units=u)
            dut.clk.value = 1
            await Timer(cycle/2, units=u)

async def reset_logic(dut, sync=True, cycles=1):
    """支持同步/异步复位的控制函数
    :param sync: True为同步复位（依赖时钟），False为异步复位
    :param cycles: 同步复位时的时钟周期数
    """
    if sync:
        await RisingEdge(dut.clk)  # 对齐时钟边沿
        dut.rst_n.value = 0
        for _ in range(cycles):
            await RisingEdge(dut.clk)
        dut.rst_n.value = 1
    else:
        dut.rst_n.value = 1
        await Timer(1, units="ns")
        dut.rst_n.value = 0
        await Timer(100, units="ns")  # 异步复位无需时钟同步
        dut.rst_n.value = 1


@cocotb.test()
async def dff_simple_test(dut):
    # clock
    await cocotb.start(generate_clock(dut,20,"us",0))

    reset_task = cocotb.start_soon(reset_logic(dut,False,10))
    
    # Set initial input value to prevent it from floating
    dut.d.value = 0  

    #reset
    await reset_task

    # Synchronize with the clock. This will regisiter the initial `d` value
    await RisingEdge(dut.clk)
    expected_val = 0  # Matches initial input value
    for i in range(10):
        dut._log.info(f"Current clk cycle: {int(dut.u_dff.cnt.value)}")  # 打印时钟周期
        val = random.randint(0, 1)
        dut.d.value = val  # Assign the random value val to the input port d
        await RisingEdge(dut.clk)
        assert dut.q.value == expected_val, f"output q was incorrect on the {i}th cycle"
        expected_val = val  # Save random value for next RisingEdge
    
    # Check the final input on the next clock
    await RisingEdge(dut.clk)  # wait for falling edge/"negedge"
    assert dut.q.value == expected_val, "output q was incorrect on the last cycle"
