# [H] Authenticated SQL injection vulnerability in reports_user.php in Cacti

## Summary
Severity: High
Advisory: CVE-2023-39358
Aliases: GHSA-gj95-7xr8-9p7g
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-05
Source: https://osv.dev/vulnerability/CVE-2023-39358
Type: osv

## Details
Cacti is an open source operational monitoring and fault management framework. An authenticated SQL injection vulnerability was discovered which allows authenticated users to perform privilege escalation and remote code execution. The vulnerability resides in the `reports_user.php` file. In `ajax_get_branches`, the `tree_id` parameter is passed to the `reports_get_branch_select` function without any validation. This issue has been addressed in version 1.2.25. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CFH3J2WVBKY4ZJNMARVOWJQK6PSLPHFH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WOQFYGLZBAWT4AWNMO7DU73QXWPXTCKH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WZGB2UXJEUYWWA6IWVFQ3ZTP22FIHMGN/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39358.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-gj95-7xr8-9p7g
- https://nvd.nist.gov/vuln/detail/CVE-2023-39358
