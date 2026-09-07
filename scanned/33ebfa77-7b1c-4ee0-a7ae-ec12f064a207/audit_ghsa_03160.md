# [C] Prototype Pollution in arr-flatten-unflatten

## Summary
Severity: Critical
Advisory: GHSA-w8f3-pvx4-4c3h
CVE: CVE-2020-7713
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-w8f3-pvx4-4c3h
Type: github-advisory

## Affected
- npm: `arr-flatten-unflatten` — affected >=0

## Details
All versions of package arr-flatten-unflatten up to and including version 1.1.4 are vulnerable to Prototype Pollution via the constructor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7713
- https://github.com/Quernest/arr-flatten-unflatten/pull/8
- https://github.com/Quernest/arr-flatten-unflatten/commit/cb4351c75f87a4fbec3b6140c40ee2993f574372
- https://snyk.io/vuln/SNYK-JS-ARRFLATTENUNFLATTEN-598396
