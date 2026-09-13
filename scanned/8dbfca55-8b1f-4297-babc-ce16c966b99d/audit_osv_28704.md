# [M] dyndbg: fix old BUG_ON in >control parser

## Summary
Severity: Medium
Advisory: CVE-2024-35947
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35947
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.314, >=4.20.0 <5.4.276, >=5.5.0 <5.10.217, >=5.11.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

dyndbg: fix old BUG_ON in >control parser

Fix a BUG_ON from 2009.  Even if it looks "unreachable" (I didn't
really look), lets make sure by removing it, doing pr_err and return
-EINVAL instead.

## References
- https://git.kernel.org/stable/c/00e7d3bea2ce7dac7bee1cf501fb071fd0ea8f6c
- https://git.kernel.org/stable/c/343081c21e56bd6690d342e2f5ae8c00183bf081
- https://git.kernel.org/stable/c/3c718bddddca9cbef177ac475b94c5c91147fb38
- https://git.kernel.org/stable/c/41d8ac238ab1cab01a8c71798d61903304f4e79b
- https://git.kernel.org/stable/c/529e1852785599160415e964ca322ee7add7aef0
- https://git.kernel.org/stable/c/a66c869b17c4c4dcf81d273b02cb0efe88e127ab
- https://git.kernel.org/stable/c/a69e1bdd777ce51061111dc419801e8a2fd241cc
- https://git.kernel.org/stable/c/ba3c118cff7bcb0fe6aa84ae1f9080d50e31c561
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OTB4HWU2PTVW5NEYHHLOCXDKG3PYA534/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35947.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35947
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
