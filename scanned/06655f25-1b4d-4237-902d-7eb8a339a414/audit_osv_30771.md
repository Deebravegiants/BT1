# [M] drm/modes: Avoid divide by zero harder in drm_mode_vrefresh()

## Summary
Severity: Medium
Advisory: CVE-2024-56369
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-56369
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.15.176, >=5.16.0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/modes: Avoid divide by zero harder in drm_mode_vrefresh()

drm_mode_vrefresh() is trying to avoid divide by zero
by checking whether htotal or vtotal are zero. But we may
still end up with a div-by-zero of vtotal*htotal*...

## References
- https://git.kernel.org/stable/c/47c8b6cf1d08f0ad40d7ea7b025442e51b35ee1f
- https://git.kernel.org/stable/c/69fbb01e891701e6d04db1ddb5ad49e42c4dd963
- https://git.kernel.org/stable/c/9398332f23fab10c5ec57c168b44e72997d6318e
- https://git.kernel.org/stable/c/b39de5a71bac5641d0fda33d1cf5682d82cf1ae5
- https://git.kernel.org/stable/c/e7c7b48a0fc5ed83baae400a1b15e33978c25d7f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56369.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56369
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
