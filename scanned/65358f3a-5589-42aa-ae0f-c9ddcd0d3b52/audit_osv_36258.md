# [C] FlaskBB Logic Flaw Authorization Group Deletion via Bulk AJAX Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-22660
Aliases: GHSA-r9cf-jxr6-5h3r
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-22660
Type: osv

## Details
FlaskBB through 2.2.0, fixed in commit a5da9a5, contains a logic flaw vulnerability that allows authenticated administrators to delete all built-in authorization groups by exploiting a type mismatch in the bulk delete protection check. The bulk AJAX endpoint in the management views compares received JSON integer group IDs against string literals, causing the protection check to always pass, which allows deletion of all six built-in groups and destroys the forum's permission model, potentially rendering the site unusable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22660.json
- https://github.com/flaskbb/flaskbb/security/advisories/GHSA-r9cf-jxr6-5h3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-22660
- https://www.vulncheck.com/advisories/flaskbb-logic-flaw-authorization-group-deletion-via-bulk-ajax-endpoint
- https://github.com/flaskbb/flaskbb/commit/a5da9a529adddc65fe31e275192b642a4e32de64
- https://github.com/flaskbb/flaskbb
