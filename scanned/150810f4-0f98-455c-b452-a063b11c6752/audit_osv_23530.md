# [M] drm/panel: ili9341: fix optional regulator handling

## Summary
Severity: Medium
Advisory: CVE-2022-49071
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49071
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panel: ili9341: fix optional regulator handling

If the optional regulator lookup fails, reset the pointer to NULL.
Other functions such as mipi_dbi_poweron_reset_conditional() only do
a NULL pointer check and will otherwise dereference the error pointer.

## References
- https://git.kernel.org/stable/c/28dc1503a9d36654f9c61adb2915682515a30f71
- https://git.kernel.org/stable/c/4ea189854b1e625ed5ec80d30147870f984db44c
- https://git.kernel.org/stable/c/d14eb80e27795b7b20060f7b151cdfe39722a813
- https://git.kernel.org/stable/c/e3d982c111a6c033671dd6084b07f62fbf50f76f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49071.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49071
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
