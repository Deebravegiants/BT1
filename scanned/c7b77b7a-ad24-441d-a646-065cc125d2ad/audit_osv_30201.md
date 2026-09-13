# [M] remoteproc: k3-r5: Fix error handling when power-up failed

## Summary
Severity: Medium
Advisory: CVE-2024-50176
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50176
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.10.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

remoteproc: k3-r5: Fix error handling when power-up failed

By simply bailing out, the driver was violating its rule and internal
assumptions that either both or no rproc should be initialized. E.g.,
this could cause the first core to be available but not the second one,
leading to crashes on its shutdown later on while trying to dereference
that second instance.

## References
- https://git.kernel.org/stable/c/7afb5e3aa989c479979faeb18768a67889a7a9c6
- https://git.kernel.org/stable/c/87ab3af7447791d0c619610fd560bd804549e187
- https://git.kernel.org/stable/c/9ab27eb5866ccbf57715cfdba4b03d57776092fb
- https://git.kernel.org/stable/c/afd102bde99d90ef41e043c846ea34b04433eb7b
- https://git.kernel.org/stable/c/fc71c23958931713b5e76f317b76be37189f2516
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50176.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50176
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
