`timescale 1ns/1ns

import dff_pkg::*;

module tb_top#(
    parameter A = 1,
    parameter B = 32'h12345678
);

logic [32 -1:0] dat_test;
logic [32 -1:0] pkg_test;

logic clk, d, rst_n;
logic q;

always_ff @(posedge clk or negedge rst_n)begin
    if(!rst_n)
        dat_test <= 'd0;
    else
        dat_test <= A;
end

always_ff @(posedge clk or negedge rst_n)begin
    if(!rst_n)
        pkg_test <= 'd0;
    else
        pkg_test <= TEST_PKG;
end

dff u_dff(
    .clk    ( clk   ),
    .d      ( d     ),
    .rst_n  ( rst_n ),
    .q      (  q    )
);

`ifdef VCS_ENABLE
initial begin
    if($test$plusargs("WAVES"))begin
        $fsdbDumpfile("tb_top.fsdb");
        $fsdbDumpvars(0, tb_top,"+all");
    end
end
`endif

endmodule