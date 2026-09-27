# [M] CVE-2021-47244

## Summary
Severity: Medium
Advisory: CVE-2021-47244
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47244
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: Fix out of bounds when parsing TCP options

The TCP option parser in mptcp (mptcp_get_options) could read one byte
out of bounds. When the length is 1, the execution flow gets into the
loop, reads one byte of the opcode, and if the opcode is neither
TCPOPT_EOL nor TCPOPT_NOP, it reads one more byte, which exceeds the
length of 1.

This fix is inspired by commit 9609dad263f8 ("ipv4: tcp_input: fix stack
out of bounds when parsing TCP options.").

## References
- https://git.kernel.org/stable/c/07718be265680dcf496347d475ce1a5442f55ad7
- https://git.kernel.org/stable/c/73eeba71dc9932970befa009e68272a3d5ec4a58
- https://git.kernel.org/stable/c/76e02b8905d0691e89e104a882f3bba7dd0f6037
