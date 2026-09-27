# [H] net/smc: check return value of sock_recvmsg when draining clc data

## Summary
Severity: High
Advisory: CVE-2024-57791
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57791
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: check return value of sock_recvmsg when draining clc data

When receiving clc msg, the field length in smc_clc_msg_hdr indicates the
length of msg should be received from network and the value should not be
fully trusted as it is from the network. Once the value of length exceeds
the value of buflen in function smc_clc_wait_msg it may run into deadloop
when trying to drain the remaining data exceeding buflen.

This patch checks the return value of sock_recvmsg when draining data in
case of deadloop in draining.

## References
- https://git.kernel.org/stable/c/6b80924af6216277892d5f091f5bfc7d1265fa28
- https://git.kernel.org/stable/c/7a6927814b4256d603e202ae7c5e38db3b338896
- https://git.kernel.org/stable/c/82c7ad9ca09975aae737abffd66d1ad98874c13d
- https://git.kernel.org/stable/c/c5b8ee5022a19464783058dc6042e8eefa34e8cd
- https://git.kernel.org/stable/c/d7d1f986ebb284b1db8dafca7d1bdb6dd2445cf6
- https://git.kernel.org/stable/c/df3dfe1a93c6298d8c09a18e4fba19ef5b17763b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57791.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57791
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
