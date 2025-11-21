// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0

// `timescale 1us/1us
import dff_pkg::*;
module dff (
    input logic clk, d, rst_n,
    output logic q
);
logic [32 -1:0] test_pkg;

always @(posedge clk or negedge rst_n) begin
    if(!rst_n)
        q <= 0;
    else
        q <= d;
end

logic [31:0] cnt;
always @(posedge clk or negedge rst_n)begin
    if(!rst_n)
        cnt <= 'd0;
    else
        cnt <= cnt + 1'b1;
end

always @(posedge clk or negedge rst_n)begin
    if(!rst_n)
        test_pkg <= 'd0;
    else
        test_pkg <= TEST_PKG1;
end

endmodule