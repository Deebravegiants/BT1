# [H] drm/imagination: take paired job reference

## Summary
Severity: High
Advisory: CVE-2025-37763
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37763
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/imagination: take paired job reference

For paired jobs, have the fragment job take a reference on the
geometry job, so that the geometry job cannot be freed until
the fragment job has finished with it.

The geometry job structure is accessed when the fragment job is being
prepared by the GPU scheduler. Taking the reference prevents the
geometry job being freed until the fragment job no longer requires it.

Fixes a use after free bug detected by KASAN:

[  124.256386] BUG: KASAN: slab-use-after-free in pvr_queue_prepare_job+0x108/0x868 [powervr]
[  124.264893] Read of size 1 at addr ffff0000084cb960 by task kworker/u16:4/63

## References
- https://git.kernel.org/stable/c/4ba2abe154ef68f9612eee9d6fbfe53a1736b064
- https://git.kernel.org/stable/c/b5a6f97a78e2fc008fd6503b7040cb7e1120b873
- https://git.kernel.org/stable/c/c90b95e12eb88d23740e5ea2c43d71675d17ac8d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37763.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37763
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
