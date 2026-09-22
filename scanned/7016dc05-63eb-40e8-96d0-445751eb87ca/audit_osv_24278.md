# [H] drm/msm/a6xx: Fix kvzalloc vs state_kcalloc usage

## Summary
Severity: High
Advisory: CVE-2022-50867
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2022-50867
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/a6xx: Fix kvzalloc vs state_kcalloc usage

adreno_show_object() is a trap!  It will re-allocate the pointer it is
passed on first call, when the data is ascii85 encoded, using kvmalloc/
kvfree().  Which means the data *passed* to it must be kvmalloc'd, ie.
we cannot use the state_kcalloc() helper.

This partially reverts commit ec8f1813bf8d ("drm/msm/a6xx: Replace
kcalloc() with kvzalloc()"), but adds the missing kvfree() to fix the
memory leak that was present previously.  And adds a warning comment.

Patchwork: https://patchwork.freedesktop.org/patch/507014/

## References
- https://git.kernel.org/stable/c/4b1bbc0571a5d7ee10f754186dc3d619b9ced5c1
- https://git.kernel.org/stable/c/83d18e9d9c0150d98dc24e3642ea93f5e245322c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50867.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50867
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
