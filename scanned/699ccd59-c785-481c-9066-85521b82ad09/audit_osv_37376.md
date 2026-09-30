# [H] dmaengine: idxd: Fix possible invalid memory access after FLR

## Summary
Severity: High
Advisory: CVE-2026-31442
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31442
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: Fix possible invalid memory access after FLR

In the case that the first Function Level Reset (FLR) concludes
correctly, but in the second FLR the scratch area for the saved
configuration cannot be allocated, it's possible for a invalid memory
access to happen.

Always set the deallocated scratch area to NULL after FLR completes.

## References
- https://git.kernel.org/stable/c/504c0e6751001ac46917c73e703f2b1b92cfc026
- https://git.kernel.org/stable/c/867d0c801f21370d561420fa32f2ea1a7dc3a22d
- https://git.kernel.org/stable/c/d6077df7b75d26e4edf98983836c05d00ebabd8d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31442.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31442
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
