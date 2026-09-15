# [H] CVE-2021-47243

## Summary
Severity: High
Advisory: CVE-2021-47243
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47243
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

sch_cake: Fix out of bounds when parsing TCP options and header

The TCP option parser in cake qdisc (cake_get_tcpopt and
cake_tcph_may_drop) could read one byte out of bounds. When the length
is 1, the execution flow gets into the loop, reads one byte of the
opcode, and if the opcode is neither TCPOPT_EOL nor TCPOPT_NOP, it reads
one more byte, which exceeds the length of 1.

This fix is inspired by commit 9609dad263f8 ("ipv4: tcp_input: fix stack
out of bounds when parsing TCP options.").

v2 changes:

Added doff validation in cake_get_tcphdr to avoid parsing garbage as TCP
header. Although it wasn't strictly an out-of-bounds access (memory was
allocated), garbage values could be read where CAKE expected the TCP
header if doff was smaller than 5.

## References
- https://git.kernel.org/stable/c/3371392c60e2685af30bd4547badd880f5df2b3f
- https://git.kernel.org/stable/c/3b491dd593d582ceeb27aa617600712a6bd14246
- https://git.kernel.org/stable/c/4cefa061fc63f4d2dff5ab4083f43857cd7a2335
- https://git.kernel.org/stable/c/595897ef118d6fe66690c4fc5b572028c9da95b7
- https://git.kernel.org/stable/c/ba91c49dedbde758ba0b72f57ac90b06ddf8e548
