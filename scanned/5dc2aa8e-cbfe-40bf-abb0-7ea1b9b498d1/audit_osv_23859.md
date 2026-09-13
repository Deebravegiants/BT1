# [M] tcp: Fix data-races around sysctl_tcp_fastopen_blackhole_timeout.

## Summary
Severity: Medium
Advisory: CVE-2022-49585
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49585
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_fastopen_blackhole_timeout.

While reading sysctl_tcp_fastopen_blackhole_timeout, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/021266ec640c7a4527e6cd4b7349a512b351de1d
- https://git.kernel.org/stable/c/0dc2f19d8c2636cebda7976b5ea40c6d69f0d891
- https://git.kernel.org/stable/c/8afa5604e295046c02b79ccf9e2bbbf8d969d60e
- https://git.kernel.org/stable/c/a77a75a0e7f397550ab039f96115103e78dd5c69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49585.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49585
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
