# [C] Prototype Pollution in worksmith

## Summary
Severity: Critical
Advisory: GHSA-9829-jj5p-j6hf
CVE: CVE-2020-7725
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-9829-jj5p-j6hf
Type: github-advisory

## Affected
- npm: `worksmith` — affected >=0

## Details
All versions up to and including 1.0.0 of the package worksmith are vulnerable to Prototype Pollution via the setValue function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7725
- https://snyk.io/vuln/SNYK-JS-WORKSMITH-598798
