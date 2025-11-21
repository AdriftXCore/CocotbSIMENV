'''
Author:zhanghx(https://github.com/AdriftXCore)
date:2025-11-18 10:27:12
'''
import os,shutil
import pytest
from pathlib import Path
import re
import cocotb_test.simulator
def safe_test_name(name):
    return re.sub(r'[^A-Za-z0-9_]', '_', name).rstrip('_')
def verilog_literal_to_hex(verilog_str):
    match = re.match(r"\d+'h([0-9a-fA-F]+)", verilog_str)
    if match:
        hex_str = match.group(1)
        return int(hex_str, 16)
    else:
        raise ValueError(f"Invalid Verilog literal: {verilog_str}")

# @pytest.fixture(scope="session", autouse=True)
# def clean_sim_build():
#     sim_build_path = Path(f'{tests_dir}/sim_build').resolve()
#     if os.path.exists(sim_build_path):
#         shutil.rmtree(sim_build_path)

def afx_test_run(
    request,
    sim: str = "vcs",
    wave: str = "1",
    ctb: str = "cocotb_top",
    tc: str = "tb_top",
    filelist: str = '../sim/filelist',
    tests_dir: str = '../sim/',
    include_list: str = '../../design/incl',
    tb_list:str = '../../verify/tb',
    rtl:str = '../../design/rtl',
    sim_ip:str = '../ip',
    parameters: dict[str, int] = {}
) -> None:
    """
    Run a cocotb-based testbench simulation.

    Args:
        ctb (str): Name of the cocotb Python module (e.g., "cocotb_top_transport_dma").
        tc (str): Name of the Verilog/SystemVerilog top testbench module.
        filelist (str): Path to the filelist (.f) file.
        tests_dir (str): Directory for simulation outputs and Python test files.
        include_list (str): Include path for SystemVerilog headers.
        tb_list (str): Directory where testbench source files are located.
        rtl (str): Directory containing RTL source files.
        parameters (Dict[str, int], optional): Parameter key-value pairs for the DUT.
        sim (str, optional): Simulator to use ("vcs" or "iverilog").
        waves (str): "1" to enable waveform dumping, "0" otherwise.
        test_name (str, optional): Test name, typically `request.node.name` from pytest.

    Returns:
        None
    """
    worker_id = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    filelist_path = Path(filelist+worker_id+".f").resolve()
    include_path = Path(include_list).resolve()
    simulation_path  = Path(f'{tests_dir}/simulate.do').resolve()
    sim_path = Path(tests_dir).resolve()
    tb_files = Path(os.path.join(tb_list, tc) + ".sv").resolve()
    dut = tc
    module = ctb
    toplevel = dut

    # simulator = os.environ.get("SIM", "").lower()
    # waves = os.environ.get("WAVES", "").lower()

    simulator = sim.lower()
    waves = wave.lower()
    verilog_sources  = []
    if os.path.exists(filelist_path):
        os.remove(filelist_path)
    rtl_path = Path(rtl)
    sim_ip_path = Path(sim_ip)
    with open(filelist_path, 'w') as f:
        for filepath in rtl_path.rglob('*'):
            if filepath.suffix in ['.v', '.sv']:
                f.write(str(filepath.resolve()) + '\n')

        for filepath in sim_ip_path.rglob('*'):
            if filepath.suffix in ['.v', '.sv']:
                f.write(str(filepath.resolve()) + '\n')


    with open(filelist_path, 'r') as f:
        for line in f:
            rel_path = line.strip()
            if rel_path:
                verilog_sources.append(rel_path)

    verilog_sources.append(str(Path(tc + '.sv').resolve()))
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}

    sim_build = os.path.join(sim_path, "sim_build",f"{safe_test_name(request.node.name)}_{worker_id}")

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
            compile_args.append("+define+VCS_ENABLE")
            extra_env["VCS_ENABLE"]="1"
            makefile_path = os.path.join(sim_build, "Makefile")
            os.makedirs(os.path.dirname(makefile_path), exist_ok=True)
            with open(makefile_path, 'w') as makefile:
                makefile.write(f"""verdi: 
\tverdi \\
\t-sv \\
\t+v2k \\
\t+incdir+{include_path} \\
\t{str(tb_files)} \\
\t-F {str(filelist_path)} \\
\t-ssf {tc}.fsdb \\
\t-nologo &
                """)
        compile_args.extend([
            "-full64",
            "+v2k",
            "-work xil_defaultlib",
            f"+incdir+{include_path}",
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
        # print(compile_args)
        sim_args = [
            "+WAVES",
            "-ucli",
            "-licqueue",
            "-l", "simulate.log",
            "-do", f"{simulation_path}"
        ]
        cocotb_test.simulator.run(
            python_search=[str(tb_files)],
            verilog_sources=verilog_sources,
            toplevel=toplevel,
            module=module,
            compile_args=compile_args,
            sim_args=sim_args,
            parameters=parameters,
            sim_build=sim_build,
            extra_env=extra_env,
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
\t+incdir+{include_path} \\
\t{str(tb_files)} \\
\t-F {str(filelist_path)} \\
\t-ssf {tc}.vcd \\
\t-nologo &

gtk:
\tgtkwave {tc}.fst 
                """)
        cocotb_test.simulator.run(
            python_search=[str(tb_files)],
            verilog_sources=verilog_sources,
            includes=[str(include_path)],
            toplevel=toplevel,
            module=module,
            extra_env=extra_env,
            parameters=parameters,
            sim_build=sim_build,
            waves=waves
        )


