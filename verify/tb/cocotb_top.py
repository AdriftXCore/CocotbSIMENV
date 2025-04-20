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


import os,shutil
from pathlib import Path
import re
import cocotb_test.simulator
def safe_test_name(name):
    return re.sub(r'[^A-Za-z0-9_]', '_', name).rstrip('_')

def test_run(request):
    # os.environ["SIM"] = "vcs"
    os.environ["WAVES"] = "1"

    ctb = "cocotb_top"
    tc = "tb_top"
    filelist = '../sim/filelist.f'
    tests_dir = '../sim/'
    include_list = '../../design/incl'
    tb_list = '../../verify/tb'
    rtl = '../../design/rtl'

    filelist_path = Path(filelist).resolve()
    sim_build_path = Path(f'{tests_dir}/sim_build').resolve()
    simulation_path  = Path(f'{tests_dir}/simulate.do').resolve()
    tb_files = Path(os.path.join(tb_list, tc) + ".sv").resolve()
    dut = tc
    module = ctb
    toplevel = dut

    simulator = os.environ.get("SIM", "").lower()
    waves = os.environ.get("WAVES", "").lower()

    verilog_sources  = []
    if os.path.exists(filelist_path):
        os.remove(filelist_path)
    if os.path.exists(sim_build_path):
        shutil.rmtree(sim_build_path)
    rtl_path = Path(rtl)
    with open(filelist_path, 'w') as f:
        for filepath in rtl_path.rglob('*'):
            if filepath.suffix in ['.v', '.sv']:
                f.write(str(filepath.resolve()) + '\n')


    with open(filelist_path, 'r') as f:
        for line in f:
            rel_path = line.strip()
            if rel_path:
                verilog_sources.append(rel_path)

    parameters = {}

    verilog_sources.append(str(Path(tc + '.sv').resolve()))
    sim_build = os.path.join(tests_dir, "sim_build",safe_test_name(request.node.name))

    if(simulator == "vcs"):
        compile_args = []
        verdi_home = os.environ.get("VERDI_HOME")
        vcs_lib_dir = os.path.join(sim_build, "vcs_lib")
        if not os.path.exists(vcs_lib_dir):
            os.makedirs(vcs_lib_dir)
        xil_defaultlib_dir = os.path.join(vcs_lib_dir, "xil_defaultlib")
        if not os.path.exists(xil_defaultlib_dir):
            os.makedirs(xil_defaultlib_dir)
        xil_defaultlib_dir = Path(xil_defaultlib_dir).resolve()
        if(waves == "1"):
            compile_args= ["+define+WAVES"]
            makefile_path = os.path.join(sim_build, "Makefile")
            os.makedirs(os.path.dirname(makefile_path), exist_ok=True)
            with open(makefile_path, 'w') as makefile:
                makefile.write(f"""verdi: 
\tverdi \\
\t-sv \\
\t+v2k \\
\t{str(tb_files)} \\
\t-F {str(filelist_path)} \\
\t-ssf {tc}.fsdb \\
\t-nologo &
                """)
        compile_args.extend([
            "-full64",
            "+v2k",
            "-work xil_defaultlib",
            f"+incdir+${include_list}",
            "-sverilog",
            "+define+SIMULATION_EN",
            "-debug_access+all+fsdb",
            "-debug_region+cell+encryp",
            "-kdb",
            f"{tb_files}",
            f"-F {filelist_path}",
            "-cpp", "g++-4.8",
            "-cc", "gcc-4.8",
            "-LDFLAGS", "-Wl,--no-as-needed",
            "-l","com.log ",
            f"-Mdir={xil_defaultlib_dir}",
            f"-P {verdi_home}/share/PLI/VCS/LINUX64/novas.tab {verdi_home}/share/PLI/VCS/LINUX64/pli.a xil_defaultlib.{tc}",
            "-o simv"
        ])
        print(compile_args)
        sim_args = [
            "-ucli",
            "-licqueue",
            "-l", "simulate.log",
            "-do", f"{simulation_path}"
        ]
        cocotb_test.simulator.run(
            python_search=[tests_dir],
            verilog_sources=verilog_sources,
            toplevel=toplevel,
            module=module,
            compile_args=compile_args,
            sim_args=sim_args,
            parameters=parameters,
            sim_build=sim_build,
            waves=waves
        )
    else:
        if(waves == "1"):
            makefile_path = os.path.join(sim_build, "Makefile")
            os.makedirs(os.path.dirname(makefile_path), exist_ok=True)
            with open(makefile_path, 'w') as makefile:
                makefile.write(f"""verdi: 
\tfst2vcd {tc}.fst -o {tc}.vcd
\tverdi \\
\t-sv \\
\t+v2k \\
\t{str(tb_files)} \\
\t-F {str(filelist_path)} \\
\t-ssf {tc}.vcd \\
\t-nologo &

gtk:
\tgtkwave {tc}.fst 
                """)
        cocotb_test.simulator.run(
            python_search=[tests_dir],
            verilog_sources=verilog_sources,
            toplevel=toplevel,
            module=module,
            parameters=parameters,
            sim_build=sim_build,
            waves=waves
        )