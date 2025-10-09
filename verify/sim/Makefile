verdi_opts = -P $(VERDI_HOME)/share/PLI/VCS/LINUX64/novas.tab $(VERDI_HOME)/share/PLI/VCS/LINUX64/pli.a
VCS_VIP_SO = $(shell cocotb-config --lib-name-path vpi vcs)
GLBL_PATH  = /opt/vivado/glbl.v

# Makefile
ctb ?= cocotb_top
tc ?= tb_top

tb_list	= $(abspath ../../verify/tb)
tb_files = $(tb_list)/$(tc).sv
rtl_list = $(abspath ../../design/rtl)
commonip_list = $(abspath ../../design/common_ip)
include_list = $(abspath ../../design/incl)

# defaults
SIM ?= vcs 
MCCB ?= 1
TOPLEVEL_LANG ?= verilog

# use VHDL_SOURCES for VHDL files
VERILOG_SOURCES += $(tb_files)
VERILOG_SOURCES += $(shell cat ./filelist.f 2>/dev/null)

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = $(tc)

# MODULE is the basename of the Python test file
export PYTHONPATH := $(PYTHONPATH):$(PWD)/..
MODULE = tb.$(ctb)

# 指定VCS编译选项
EXTRA_ARGS += -full64 -cpp g++-4.8 -cc gcc-4.8 -LDFLAGS "-Wl,--no-as-needed" -debug_access+all +incdir+${include_list} -f $(abspath ./filelist.f)

SIM_ARGS += +vpi -P ./pli.tab -load $(VCS_VIP_SO):cocotbvpi_entry_point

# include cocotb's make rules to take care of the simulator setup
ifeq ($(MCCB),1)
include $(shell cocotb-config --makefiles)/Makefile.sim
endif

# 默认目标：生成文件列表后启动仿真
test:
	cd $(tb_list) && pytest $(tb_list)/$(ctb).py -v

all: clean_all mklist compile elaborate run
				# $(MAKE) sim

allv: all verdi

# 定义clean操作
clean_all:
				rm -rf  ./stack.info* *.key *.vpd DVEfiles coverage *.vdb *.vcd *.xml novas* verdiLog vfastLog *.mr *.pvl *.syn *.svf ./filelist.f simv.daidir *.log *.fsdb *.fsdb.*  simv vcs_lib 64 sim_build $(PWD)/../tb/__pycache__ $(PWD)/../tb/.pytest_cache


# 定义mklist操作
mklist:
				rm -rf ./filelist.f
				touch ./filelist.f
				find  $(rtl_list) -type f \( -name "*.v" -o -name "*.sv" \) >> filelist.f

compile:
				vlogan \
				+v2k \
				-assert svaext \
				-full64 \
				-work xil_defaultlib \
				$(GLBL_PATH) \
				+incdir+${include_list} \
				-sverilog \
				+define+SIMULATION_EN \
				+define+WAVES \
				$(tb_files) \
				-F ./filelist.f \
				-l com.log \

elaborate:
				vcs \
				-assert svaext \
				-full64 \
				-cpp g++-4.8 -cc gcc-4.8 -LDFLAGS -Wl,--no-as-needed \
				-Mdir=./vcs_lib/xil_defaultlib \
				-sverilog \
			    -debug_acc+all -debug_region+cell+encrypt \
				$(verdi_opts) \
				xil_defaultlib.${tc} xil_defaultlib.glbl\
				+vpi -P ./pli.tab -load $(VCS_VIP_SO):cocotbvpi_entry_point \
				-o simv \
				2>&1 | tee -a vlogan.log

run:
				./simv -ucli -licqueue -l simulate.log -do simulate.do

verdi:
	@read -p "Open Verdi? (y/n): " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		echo "Launching Verdi..."; \
		verdi \
			-sv \
			+v2k \
			$(tb_files) \
			+incdir+${include_list} \
			-F ./filelist.f \
			-ssf $(tc).fsdb \
			-nologo & \
	else \
		echo "Verdi launch canceled."; \
	fi

