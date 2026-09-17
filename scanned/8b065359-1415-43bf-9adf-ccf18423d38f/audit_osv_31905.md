# [M] cifs: Fix integer overflow while processing closetimeo mount option

## Summary
Severity: Medium
Advisory: CVE-2025-21962
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21962
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.180, >=5.16.0 <6.1.132, >=6.0.0 <6.6.84, >=6.2.0 <6.12.20, >=6.7.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: Fix integer overflow while processing closetimeo mount option

User-provided mount parameter closetimeo of type u32 is intended to have
an upper limit, but before it is validated, the value is converted from
seconds to jiffies which can lead to an integer overflow.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/1c46673be93dd2954f44fe370fb4f2b8e6214224
- https://git.kernel.org/stable/c/513f6cf2e906a504b7ab0b62b2eea993a6f64558
- https://git.kernel.org/stable/c/6c13fcb7cf59ae65940da1dfea80144e42921e53
- https://git.kernel.org/stable/c/9968fcf02cf6b0f78fbacf3f63e782162603855a
- https://git.kernel.org/stable/c/b24edd5c191c2689c59d0509f0903f9487eb6317
- https://git.kernel.org/stable/c/d5a30fddfe2f2e540f6c43b59cf701809995faef
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21962.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21962
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
