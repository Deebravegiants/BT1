# [M] CVE-2022-3113

## Summary
Severity: Medium
Advisory: CVE-2022-3113
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3113
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. mtk_vcodec_fw_vpu_init in drivers/media/platform/mtk-vcodec/mtk_vcodec_fw_vpu.c lacks check of the return value of devm_kzalloc() and will cause the null pointer dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=e25a89f743b18c029bfbe5e1663ae0c7190912b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3113.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3113
- https://bugzilla.redhat.com/show_bug.cgi?id=2153053
