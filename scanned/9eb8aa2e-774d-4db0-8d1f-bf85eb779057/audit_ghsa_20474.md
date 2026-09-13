# [H] Uncontrolled Resource Consumption in parse-link-header

## Summary
Severity: High
Advisory: GHSA-q674-xm3x-2926
CVE: CVE-2021-23490
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-q674-xm3x-2926
Type: github-advisory

## Affected
- npm: `parse-link-header` — affected >=0 <2.0.0

## Details
The package parse-link-header before 2.0.0 are vulnerable to Regular Expression Denial of Service (ReDoS) via the checkHeader function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23490
- https://github.com/thlorenz/parse-link-header/commit/72f05c717b3f129c5331a07bf300ed8886eb8ae1
- https://github.com/thlorenz/parse-link-header
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2321973
- https://snyk.io/vuln/SNYK-JS-PARSELINKHEADER-1582783
