# [H] Cross-site Scripting in OctoPrint

## Summary
Severity: High
Advisory: GHSA-x7r7-wmj8-vv5g
CVE: CVE-2022-1430
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-19
Source: https://github.com/advisories/GHSA-x7r7-wmj8-vv5g
Type: github-advisory

## Affected
- PyPI: `OctoPrint` — affected >=0 <1.8.0

## Details
Cross-site Scripting (XSS) - DOM in GitHub repository octoprint/octoprint prior to 1.8.0. The login endpoint allows for javascript injection which may lead to account takeover in a phishing scenario.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1430
- https://github.com/octoprint/octoprint/commit/8087528e4a7ddd15c7d95ff662deb5ef7de90045
- https://github.com/advisories/GHSA-x7r7-wmj8-vv5g
- https://github.com/octoprint/octoprint
- https://github.com/pypa/advisory-database/tree/main/vulns/octoprint/PYSEC-2022-200.yaml
- https://huntr.dev/bounties/0cd30d71-1e32-4a0b-b4c3-faaa1907b541
