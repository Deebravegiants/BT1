# [H] Path Traversal in marscode

## Summary
Severity: High
Advisory: GHSA-8pww-pp5r-rff8
CVE: CVE-2020-7681
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-8pww-pp5r-rff8
Type: github-advisory

## Affected
- npm: `marscode` — affected >=0

## Details
This affects all versionsup to and including version 1.0.1-0 of package marscode. There is no path sanitization in the path provided at `fs.readFile` in `index.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7681
- https://snyk.io/vuln/SNYK-JS-MARSCODE-590122
