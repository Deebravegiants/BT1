# [M] CVE-2025-51479

## Summary
Severity: Medium
Advisory: CVE-2025-51479
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-51479
Type: osv

## Details
Authorization bypass in update_user_group in onyx-dot-app Onyx Enterprise Edition 0.27.0 allows remote authenticated attackers to modify arbitrary user groups via crafted PATCH requests to the /api/manage/admin/user-group/id endpoint, bypassing intended curator-group assignment checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51479.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51479
- https://github.com/onyx-dot-app/onyx/pull/4714
- https://github.com/onyx-dot-app/onyx
- https://www.gecko.security/blog/cve-2025-51479
