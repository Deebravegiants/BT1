# [H] OS Command Injection in compile-sass

## Summary
Severity: High
Advisory: GHSA-79qm-h35f-hr77
CVE: CVE-2019-10799
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-79qm-h35f-hr77
Type: github-advisory

## Affected
- npm: `compile-sass` — affected >=0 <1.0.5

## Details
compile-sass prior to 1.0.5 allows execution of arbritary commands. The function &quot;setupCleanupOnExit(cssPath)&quot; within &quot;dist/index.js&quot; is executed as part of the &quot;rm&quot; command without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10799
- https://github.com/eiskalteschatten/compile-sass/commit/d9ada7797ff93875b6466dea7a78768e90a0f8d2
- https://github.com/eiskalteschatten/compile-sass
- https://snyk.io/vuln/SNYK-JS-COMPILESASS-551804
- https://snyk.io/vuln/SNYK-JS-RPI-548942
