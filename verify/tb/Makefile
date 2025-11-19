ctb ?= cocotb_top
work ?= ../sim

SIM ?= icarus
WAVES ?= 1

clean_all:
	cd $(abspath $(work)) && rm -rf  ./stack.info* *.key *.vpd DVEfiles coverage *.vdb *.vcd *.xml novas* verdiLog vfastLog *.mr *.pvl *.syn *.svf ./*.f simv.daidir *.log *.fsdb *.fsdb.*  simv vcs_lib 64 sim_build $(PWD)/../tb/__pycache__ $(PWD)/../tb/.pytest_cache

run:clean_all
	SIM=$(SIM) WAVES=$(WAVES) pytest $(ctb).py -v -s --color=yes 2>&1 | tee pytest.log

runq:clean_all
	SIM=$(SIM) WAVES=$(WAVES) pytest $(ctb).py -v -s -n auto --color=yes 2>&1 | tee pytest.log
