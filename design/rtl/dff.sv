// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0

// `timescale 1us/1us

module dff (
    input logic clk, d, rst_n,
    output logic q
);

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

endmodule