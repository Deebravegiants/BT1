# [H] netfilter: ipset: Hold module reference while requesting a module

## Summary
Severity: High
Advisory: CVE-2024-56637
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56637
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ipset: Hold module reference while requesting a module

User space may unload ip_set.ko while it is itself requesting a set type
backend module, leading to a kernel crash. The race condition may be
provoked by inserting an mdelay() right after the nfnl_unlock() call.

## References
- https://git.kernel.org/stable/c/0e67805e805c1f3edd6f43adbe08ea14b552694b
- https://git.kernel.org/stable/c/456f010bfaefde84d3390c755eedb1b0a5857c3c
- https://git.kernel.org/stable/c/5bae60a933ba5d16eed55c6b279be51bcbbc79b0
- https://git.kernel.org/stable/c/6099b5d3e37145484fac4b8b4070c3f1abfb3519
- https://git.kernel.org/stable/c/90bf312a6b6b3d6012137f6776a4052ee85e0340
- https://git.kernel.org/stable/c/ba5e070f36682d07ca7ad2a953e6c9d96be19dca
- https://git.kernel.org/stable/c/e5e2d3024753fdaca818b822e3827614bacbdccf
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56637.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56637
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
