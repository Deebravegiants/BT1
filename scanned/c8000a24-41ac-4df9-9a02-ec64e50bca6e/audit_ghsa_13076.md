# [H] underscore-keypath vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-gpvc-mx6g-cchv
CVE: CVE-2023-26139
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-01
Source: https://github.com/advisories/GHSA-gpvc-mx6g-cchv
Type: github-advisory

## Affected
- npm: `underscore-keypath` — affected >=0.0.11

## Details
Versions of the package underscore-keypath from 0.0.11 are vulnerable to Prototype Pollution via the name argument of the `setProperty()` function. Exploiting this vulnerability is possible due to improper input sanitization which allows the usage of arguments like `__proto__`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26139
- https://gist.github.com/lelecolacola123/cc0d1e73780127aea9482c05f2ff3252
- https://github.com/jeeeyul/underscore-keypath
- https://security.snyk.io/vuln/SNYK-JS-UNDERSCOREKEYPATH-5416714
