'''
Author:zhanghx(https://github.com/AdriftXCore)
date:2025-03-01 23:02:10
'''
import cocotb
from cocotb.handle import SimHandle
from cocotb.triggers import *
from cocotb.result import SimTimeoutError
from cocotb.clock import Clock


async def timeout_watchdog(dut: SimHandle, timeout: int, mode: int = 0) -> None:
    if(mode == 0):
        await ClockCycles(dut.clk, timeout)
        dut._log.error(f"---------------------------------timeout:{timeout} CYCLE ---------------------------------")
    else:
        await Timer(timeout, 'us')
        dut._log.error(f"---------------------------------timeout:{timeout} us ---------------------------------")
    raise SimTimeoutError


@cocotb.test()
async def dff_simple_test(dut: SimHandle):
    try:
        clock = Clock(dut.clk, period=10, units="ns")
        cocotb.start_soon(clock.start()) 
        watchdog_task = cocotb.start_soon(timeout_watchdog(dut, 1000))

        await Timer(10000, units="ns")

        await watchdog_task
        watchdog_task.kill()
    except Exception as e:
        dut._log.error(f"Check failed: {e}")
        raise
