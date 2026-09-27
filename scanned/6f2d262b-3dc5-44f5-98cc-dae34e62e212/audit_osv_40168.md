# [M] DataEase: Token with Overly Broad Privileges in Share Mode: Access to Unshared Datasets

## Summary
Severity: Medium
Advisory: CVE-2026-50530
Aliases: GHSA-qcf4-345v-6vg9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-50530
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.24, a share mode chart data interface only validates that sceneId matches the resourceId in the link token and fails to validate whether tableId and field IDs in the request body belong to the shared resource, allowing an attacker with a valid share link token to replace dataset identifiers and retrieve unauthorized data through POST /de2api/chartData/getData. This issue is fixed in version 2.10.24.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50530.json
- https://github.com/dataease/dataease/security/advisories/GHSA-qcf4-345v-6vg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-50530
- https://github.com/dataease/dataease/commit/c4e85a981e53c95b1ea73757db31e3025efdc410
