# [M] CVE-2022-3115

## Summary
Severity: Medium
Advisory: CVE-2022-3115
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3115
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. malidp_crtc_reset in drivers/gpu/drm/arm/malidp_crtc.c lacks check of the return value of kzalloc() and will cause the null pointer dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=73c3ed7495c67b8fbdc31cf58e6ca8757df31a33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3115.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3115
- https://bugzilla.redhat.com/show_bug.cgi?id=2153058
