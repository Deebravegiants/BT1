# [M] Phone information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xg5p-8wg5-rhxm
CVE: CVE-2024-22889
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-xg5p-8wg5-rhxm
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0

## Details
Due to incorrect access control in Plone version v6.0.9, remote attackers can view and list all files hosted on the website via sending a crafted request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22889
- https://github.com/plone/Plone
- https://github.com/shenhav12/CVE-2024-22889-Plone-v6.0.9
