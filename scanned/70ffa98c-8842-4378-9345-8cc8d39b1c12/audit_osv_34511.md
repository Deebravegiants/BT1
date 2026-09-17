# [M] CVE-2025-61318

## Summary
Severity: Medium
Advisory: CVE-2025-61318
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-61318
Type: osv

## Details
Emlog Pro 2.5.20 has an arbitrary file deletion vulnerability. This vulnerability stems from the admin/template.php component and the admin/plugin.php component. They fail to perform path verification and dangerous code filtering for deletion parameters, allowing attackers to exploit this feature for directory traversal.

## References
- https://github.com/AndyNull/em/blob/main/emlog%20pro%20-%20del%20vuln.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61318.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61318
