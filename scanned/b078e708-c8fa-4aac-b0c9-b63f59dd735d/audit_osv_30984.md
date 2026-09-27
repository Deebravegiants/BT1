# [H] CVE-2024-57262

## Summary
Severity: High
Advisory: CVE-2024-57262
CVSS: 7.1 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2024-57262
Type: osv

## Details
In barebox before 2025.01.0, ext4fs_read_symlink has an integer overflow for zalloc (adding one to an le32 variable) via a crafted ext4 filesystem with an inode size of 0xffffffff, resulting in a malloc of zero and resultant memory overwrite, a related issue to CVE-2024-57256.

## References
- https://git.pengutronix.de/cgit/barebox/commit/?id=a2b76550f7d8
- https://git.pengutronix.de/cgit/barebox/commit/?id=a2b76550f7d87ba6f88a9ea50e71f107b514ff4e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57262.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57262
