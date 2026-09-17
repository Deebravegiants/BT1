# [M] drm/omap: fix NULL but dereferenced coccicheck error

## Summary
Severity: Medium
Advisory: CVE-2022-49510
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49510
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/omap: fix NULL but dereferenced coccicheck error

Fix the following coccicheck warning:
./drivers/gpu/drm/omapdrm/omap_overlay.c:89:22-25: ERROR: r_ovl is NULL
but dereferenced.

Here should be ovl->idx rather than r_ovl->idx.

## References
- https://git.kernel.org/stable/c/08d9a75eab594ca508a440db7c73064498d26687
- https://git.kernel.org/stable/c/8f2a3970c969d0d8d7289a4c65edcedafc16fd92
- https://git.kernel.org/stable/c/d2507be660310bb9bcca918f81f49b8bba07e462
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49510.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49510
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
