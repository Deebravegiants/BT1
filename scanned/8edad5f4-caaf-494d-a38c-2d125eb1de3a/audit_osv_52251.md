# [H] CVE-2021-47245

## Summary
Severity: High
Advisory: CVE-2021-47245
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47245
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: synproxy: Fix out of bounds when parsing TCP options

The TCP option parser in synproxy (synproxy_parse_options) could read
one byte out of bounds. When the length is 1, the execution flow gets
into the loop, reads one byte of the opcode, and if the opcode is
neither TCPOPT_EOL nor TCPOPT_NOP, it reads one more byte, which exceeds
the length of 1.

This fix is inspired by commit 9609dad263f8 ("ipv4: tcp_input: fix stack
out of bounds when parsing TCP options.").

v2 changes:

Added an early return when length < 0 to avoid calling
skb_header_pointer with negative length.

## References
- https://git.kernel.org/stable/c/9cdf299ba4e153b5e56187648420de22c6216f02
- https://git.kernel.org/stable/c/e1eb98cfeafdd85537e7e3cefe93ca9bfbcc3ea8
- https://git.kernel.org/stable/c/f648089337cb8ed40b2bb96e244f72b9d97dc96b
- https://git.kernel.org/stable/c/576c1526b4d83c44ad7b673cb841f36cbc6cb6c4
- https://git.kernel.org/stable/c/5fc177ab759418c9537433e63301096e733fb915
- https://git.kernel.org/stable/c/674b5f0c6a4fc5d3abce877048290cea6091fcb1
- https://git.kernel.org/stable/c/6defc77d48eff74075b80ad5925061b2fc010d98
- https://git.kernel.org/stable/c/7d9a9a1a88a3da574e019b4de756bc73337b3b0b
