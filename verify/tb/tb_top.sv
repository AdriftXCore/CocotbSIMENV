`timescale 1ns/1ns

module tb_top#(
    parameter A = 0,
    parameter B = 32'h12345678
);

logic clk, d, rst_n;
logic q;

dff u_dff(
    .clk    ( clk   ),
    .d      ( d     ),
    .rst_n  ( rst_n ),
    .q      (  q    )
);

initial begin
    $fsdbDumpfile("tb_top.fsdb");
    $fsdbDumpvars(0, tb_top,"+all");
end


endmodule