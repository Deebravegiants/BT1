# [H] x86/entry_32: Clear CPU buffers after register restore in NMI return

## Summary
Severity: High
Advisory: CVE-2024-50193
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50193
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.228, >=5.11.0 <5.15.169, >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/entry_32: Clear CPU buffers after register restore in NMI return

CPU buffers are currently cleared after call to exc_nmi, but before
register state is restored. This may be okay for MDS mitigation but not for
RDFS. Because RDFS mitigation requires CPU buffers to be cleared when
registers don't have any sensitive data.

Move CLEAR_CPU_BUFFERS after RESTORE_ALL_NMI.

## References
- https://git.kernel.org/stable/c/227358e89703c344008119be7e8ffa3fdb5b92de
- https://git.kernel.org/stable/c/43778de19d2ef129636815274644b9c16e78c66b
- https://git.kernel.org/stable/c/48a2440d0f20c826b884e04377ccc1e4696c84e9
- https://git.kernel.org/stable/c/64adf22c4bc73ede920baca5defefb70f190cdbc
- https://git.kernel.org/stable/c/6f44a5fc15b5cece0785bc07453db77d99b0a6de
- https://git.kernel.org/stable/c/b6400eb0b347821efc57760221f8fb6d63b9548a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50193.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50193
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
