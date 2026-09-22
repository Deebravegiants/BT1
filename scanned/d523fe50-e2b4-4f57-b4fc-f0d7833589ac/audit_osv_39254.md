# [M] OpenProject: Improper Access Control on OpenProject through the POST request to /projects/[PROJECT_NAME]/cost_reports/[REPORT_ID]/rename

## Summary
Severity: Medium
Advisory: CVE-2026-44734
Aliases: GHSA-c767-34gh-gh2h
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-44734
Type: osv

## Details
OpenProject is open-source, web-based project management software. Prior to 17.3.2 and 17.4.0, a Missing Authorization vulnerability exists in OpenProject's CostReportsController. The rename and update actions allow any authenticated user to modify the name, filters, and grouping of any Public cost report in the system without verifying ownership or permission level. An attacker who discovers or guesses a public report's numeric ID can rename or overwrite its filter configuration without any warning to the report's owner. This vulnerability is fixed in 17.3.2 and 17.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44734.json
- https://github.com/opf/openproject/security/advisories/GHSA-c767-34gh-gh2h
- https://nvd.nist.gov/vuln/detail/CVE-2026-44734
