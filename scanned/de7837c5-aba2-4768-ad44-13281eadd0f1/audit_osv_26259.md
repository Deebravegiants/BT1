# [H] io_uring: drop any code related to SCM_RIGHTS

## Summary
Severity: High
Advisory: CVE-2023-52656
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2023-52656
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: drop any code related to SCM_RIGHTS

This is dead code after we dropped support for passing io_uring fds
over SCM_RIGHTS, get rid of it.

## References
- https://git.kernel.org/stable/c/6e5e6d274956305f1fc0340522b38f5f5be74bdb
- https://git.kernel.org/stable/c/6fc19b3d8a45ff0e5d50ec8184cee1d5eac1a8ba
- https://git.kernel.org/stable/c/88c49d9c896143cdc0f77197c4dcf24140375e89
- https://git.kernel.org/stable/c/a3812a47a32022ca76bf46ddacdd823dc2aabf8b
- https://git.kernel.org/stable/c/a6771f343af90a25f3a14911634562bb5621df02
- https://git.kernel.org/stable/c/cfb24022bb2c31f1f555dc6bc3cc5e2547446fb3
- https://git.kernel.org/stable/c/d909d381c3152393421403be4b6435f17a2378b4
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52656.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52656
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
