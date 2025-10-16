set DESINE_NAME dff

#set_option enableV05 yes
set_option enableSV yes
set_option language_mode mixed
set_option designread_enable_synthesis yes
set_option designread_disable_flatten no
set_parameter handle_large_bus yes
set_option sgsyn_loop_limit 32768
set_option mthresh 50000
set_option define_cell_sim_depth 12
set_option top $DESINE_NAME

##Goal Setup Section

read_file -type sourcelist  ../sim/rtl_filelist.f
#source read_lib.f
set_option top $DESINE_NAME
set_option use_multi_threads {synthesis}
#set_option sgsyn_max_core_count 8
current_goal Design_Read -top $DESINE_NAME
link_design -force
###########next constraint command is either-or choice
#read_file -type sgdc design.sgdc;#sgdc file

#set_option sdc2sgdc yes;#sdc file
#sdc_data -file ./results/${DESINE_NAME}.mapped.sdc  -level rtl -mode fn1
current_goal lint/lint_rtl  -top $DESINE_NAME
#run_goal
#current_goal lint/lint_rtl_enhanced   -top $DESINE_NAME
#waive -rule "STARC-2.3.4.3" -du asic_foo_wrapper_case1
#waive -rule "STARC-2.3.4.3" -du asic_bar_wrapper_case2


run_goal
current_goal  lint/lint_turbo_rtl   -top $DESINE_NAME
run_goal
current_goal  lint/lint_functional_rtl  -top $DESINE_NAME
run_goal
current_goal  lint/lint_abstract  -top $DESINE_NAME
run_goal

