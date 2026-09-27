# [C] Prototype Pollution in deeps

## Summary
Severity: Critical
Advisory: GHSA-rgfv-v3jh-7ffp
CVE: CVE-2020-7716
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-rgfv-v3jh-7ffp
Type: github-advisory

## Affected
- npm: `deeps` — affected >=0

## Details
All versions of package deeps up to and including version 1.4.5 are vulnerable to Prototype Pollution via the set function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7716
- https://snyk.io/vuln/SNYK-JS-DEEPS-598667
