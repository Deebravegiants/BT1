# [C] OS Command Injection in gulkp-styledocco

## Summary
Severity: Critical
Advisory: GHSA-h33p-5j96-w8qh
CVE: CVE-2020-7607
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-h33p-5j96-w8qh
Type: github-advisory

## Affected
- npm: `gulp-styledocco` — affected >=0

## Details
gulp-styledocco through 0.0.3 allows execution of arbitrary commands. The argument `options` of the exports function in `index.js` can be controlled by users without any sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7607
- https://snyk.io/vuln/SNYK-JS-GULPSTYLEDOCCO-560126
