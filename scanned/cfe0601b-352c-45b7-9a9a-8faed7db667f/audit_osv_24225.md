# [H] drm/msm: fix use-after-free on probe deferral

## Summary
Severity: High
Advisory: CVE-2022-50492
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2022-50492
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.12.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: fix use-after-free on probe deferral

The bridge counter was never reset when tearing down the DRM device so
that stale pointers to deallocated structures would be accessed on the
next tear down (e.g. after a second late bind deferral).

Given enough bridges and a few probe deferrals this could currently also
lead to data beyond the bridge array being corrupted.

Patchwork: https://patchwork.freedesktop.org/patch/502665/

## References
- https://git.kernel.org/stable/c/0a30a47741b6df1f9555a0fac6aebb7e8c363bad
- https://git.kernel.org/stable/c/6808abdb33bf90330e70a687d29f038507e06ebb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50492.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50492
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
