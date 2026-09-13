# [H] apparmor: Fix memleak in alloc_ns()

## Summary
Severity: High
Advisory: CVE-2022-50860
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2022-50860
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

apparmor: Fix memleak in alloc_ns()

After changes in commit a1bd627b46d1 ("apparmor: share profile name on
replacement"), the hname member of struct aa_policy is not valid slab
object, but a subset of that, it can not be freed by kfree_sensitive(),
use aa_policy_destroy() to fix it.

## References
- https://git.kernel.org/stable/c/0250cf8d37bb5201a117177afd24dc73a1c81657
- https://git.kernel.org/stable/c/12695b4b76d437b9c0182a6f7dfb2248013a9daf
- https://git.kernel.org/stable/c/5f509fa740b17307f0cba412485072f632d5af36
- https://git.kernel.org/stable/c/9a32aa87a25d800b2c6f47bc2749a7bfd9a486f3
- https://git.kernel.org/stable/c/e9e6fa49dbab6d84c676666f3fe7d360497fd65b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50860.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50860
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
