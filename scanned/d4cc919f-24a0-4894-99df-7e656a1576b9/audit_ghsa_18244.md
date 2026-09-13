# [M] Subrion CMS: Authenticated administrators are able to gain escalated access through Run SQL Query tool

## Summary
Severity: Medium
Advisory: GHSA-h8wv-vv58-468h
CVE: CVE-2025-56556
CWE: CWE-566
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-11
Source: https://github.com/advisories/GHSA-h8wv-vv58-468h
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
An issue was discovered in Subrion CMS 4.2.1, allowing authenticated adminitrators or moderators with access to the built-in Run SQL Query feature under the SQL Tool admin panel — to gain escalated privileges in the context of the SQL query tool.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56556
- https://github.com/intelliants/subrion/issues/913
- https://github.com/intelliants/subrion
