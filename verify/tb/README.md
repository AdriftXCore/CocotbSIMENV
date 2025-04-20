# READEME

## the test run
```python
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

ctb = "cocotb_top"
tc = "tb_top"
filelist = '../sim/filelist.f'
tests_dir = '../sim/'
include_list = '../../design/incl'
tb_list = '../../verify/tb'
rtl = '../../design/rtl'

@pytest.fixture(scope="session", autouse=True)
def clean_sim_build():
    sim_build_path = Path(f'{tests_dir}/sim_build').resolve()
    if os.path.exists(sim_build_path):
        shutil.rmtree(sim_build_path)


# @pytest.mark.parametrize("a", [0,1,2])
# @pytest.mark.parametrize("a", [0])
def test_run(request,a):
    # os.environ["SIM"] = "vcs"
    os.environ["WAVES"] = "1"

    parameters = {}
    parameters['A'] = a

    filelist_path = Path(filelist).resolve()
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


    verilog_sources.append(str(Path(tc + '.sv').resolve()))
    extra_env = {f'PARAM_{k}': str(v) for k, v in parameters.items()}
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
```

## example
pytest cocotb_top.py
WAVES=1 SIM=icarus pytest cocotb_top.py -v -s
WAVES=1 SIM=vcs pytest cocotb_top.py -v -s