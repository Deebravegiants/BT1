# [M] CVE-2022-3112

## Summary
Severity: Medium
Advisory: CVE-2022-3112
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3112
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. amvdec_set_canvases in drivers/staging/media/meson/vdec/vdec_helpers.c lacks check of the return value of kzalloc() and will cause the null pointer dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=c8c80c996182239ff9b05eda4db50184cf3b2e99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3112.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3112
- https://bugzilla.redhat.com/show_bug.cgi?id=2153068
