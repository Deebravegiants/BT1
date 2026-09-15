# [M] drm/sched: Fix fence reference count leak

## Summary
Severity: Medium
Advisory: CVE-2025-21995
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-21995
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.85, >=6.7.0 <6.12.21, >=6.13.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/sched: Fix fence reference count leak

The last_scheduled fence leaks when an entity is being killed and adding
the cleanup callback fails.

Decrement the reference count of prev when dma_fence_add_callback()
fails, ensuring proper balance.

[phasta: add git tag info for stable kernel]

## References
- https://git.kernel.org/stable/c/1135a9431160575466ea9ac37ebd756ecbe35fff
- https://git.kernel.org/stable/c/35399c84dcedd6d31448fb9e1336ef52673f2882
- https://git.kernel.org/stable/c/a952f1ab696873be124e31ce5ef964d36bce817f
- https://git.kernel.org/stable/c/c76bd3c99293834de7d1dca5de536616d5655e38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21995.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21995
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
