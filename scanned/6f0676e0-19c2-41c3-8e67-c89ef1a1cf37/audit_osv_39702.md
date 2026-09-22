# [H] Bludit CMS has improper authorization and mediation failure leading to persistent ghost sessions

## Summary
Severity: High
Advisory: CVE-2026-46656
Aliases: GHSA-rpq2-j9w3-h4jw
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46656
Type: osv

## Details
Bludit is a content management system. Versions prior to 3.22.0 have a Broken Access Control flaw where active sessions remain valid even after the corresponding user account has been  physically deleted from the database. This "Ghost Session" allows revoked users to maintain full unauthorized access to the system. Version 3.22.0 fixes the issue.

## References
- https://github.com/bludit/bludit/releases/tag/3.22.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46656.json
- https://github.com/bludit/bludit/security/advisories/GHSA-rpq2-j9w3-h4jw
- https://nvd.nist.gov/vuln/detail/CVE-2026-46656
- https://github.com/bludit/bludit/commit/7931d1c55a3cc535911a9901c328f0197afe1c9f
