# Makefile
ctb = cocotb_top
tc = tb_top

tb_list	= $(abspath ../../verify/tb)
tb_files = $(tb_list)/$(tc).sv
rtl_list = $(abspath ../../design/rtl)
commonip_list = $(abspath ../../design/common_ip)
include_list = $(abspath ../../design/incl)

# defaults
SIM ?= vcs 
TOPLEVEL_LANG ?= verilog

# use VHDL_SOURCES for VHDL files
VERILOG_SOURCES += $(tb_files)
VERILOG_SOURCES += $(shell cat ./filelist.f)

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = $(tc)

# MODULE is the basename of the Python test file
export PYTHONPATH := $(PYTHONPATH):$(PWD)/..
MODULE = tb.cocotb_top

# 指定VCS编译选项
EXTRA_ARGS += -full64 -cpp g++-4.8 -cc gcc-4.8 -LDFLAGS "-Wl,--no-as-needed" -debug_access+all +incdir+${include_list} -f $(abspath ./filelist.f)

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

# 默认目标：生成文件列表后启动仿真
all: clean_all mklist compile elaborate run
				$(MAKE) sim

allv: all verdi

# 定义clean操作
clean_all:
				rm -rf  *.key *.vpd DVEfiles coverage *.vdb *.vcd *.xml novas* verdiLog vfastLog *.mr *.pvl *.syn *.svf ./filelist.f simv.daidir *.log *.fsdb *.fsdb.*  simv vcs_lib 64 sim_build $(PWD)/../tb/__pycache__


# 定义mklist操作
mklist:
				rm -rf ./filelist.f
				touch ./filelist.f
				find  $(rtl_list) -type f \( -name "*.v" -o -name "*.sv" \) >> filelist.f

compile:
				vlogan \
				+v2k \
				-full64 \
				-work xil_defaultlib \
				+incdir+${include_list} \
				-sverilog \
				+define+SIMULATION_EN \
				$(tb_files) \
				-F ./filelist.f \
				-l com.log \

elaborate:
				vcs \
				-full64 \
				-cpp g++-4.8 -cc gcc-4.8 -LDFLAGS -Wl,--no-as-needed \
				-Mdir=./vcs_lib/xil_defaultlib \
				-sverilog \
			    -debug_acc+all -debug_region+cell+encrypt \
				$(verdi_opts) \
				xil_defaultlib.${tc} \
				-o simv \
				2>&1 | tee -a vlogan.log

run:
				./simv -ucli -licqueue -l simulate.log -do simulate.do

verdi:
				verdi \
				-sv \
				+v2k \
				$(tb_files) \
				-F ./filelist.f \
				-ssf *.fsdb \
				-nologo &
