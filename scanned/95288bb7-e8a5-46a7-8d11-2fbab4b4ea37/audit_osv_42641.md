# [M] SiYuan before v3.7.3 Path Traversal via unvalidated avID

## Summary
Severity: Medium
Advisory: CVE-2026-69086
Aliases: GHSA-7hm9-v7vf-7g4w, GO-2026-6373
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-69086
Type: osv

## Details
SiYuan versions before v3.7.3 fail to validate the avID parameter on all code branches in attribute-view read endpoints, allowing attackers to construct traversal paths that escape the storage directory. Authenticated users with RoleReader permissions or anonymous clients when publish authentication is disabled can read JSON files outside the attribute-view directory to disclose cross-scope database content.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69086.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-7hm9-v7vf-7g4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-69086
- https://www.vulncheck.com/advisories/siyuan-before-path-traversal-via-unvalidated-avid
