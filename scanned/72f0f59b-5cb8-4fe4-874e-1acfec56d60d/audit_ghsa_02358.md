# [M] jszip Vulnerable to Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-jg8v-48h5-wgxg
CVE: CVE-2021-23413
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-08-10
Source: https://github.com/advisories/GHSA-jg8v-48h5-wgxg
Type: github-advisory

## Affected
- npm: `jszip` — affected >=3.0.0 <3.7.0
- npm: `jszip` — affected >=0 <2.7.0

## Details
This affects the package jszip before 3.7.0. Crafting a new zip file with filenames set to Object prototype values (e.g `__proto__`, `toString`, etc) results in a returned object with a modified prototype instance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23413
- https://github.com/Stuk/jszip/pull/766
- https://github.com/Stuk/jszip/commit/22357494f424178cb416cdb7d93b26dd4f824b36
- https://github.com/Stuk/jszip
- https://github.com/Stuk/jszip/blob/master/lib/object.js%23L88
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1251499
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1251498
- https://snyk.io/vuln/SNYK-JS-JSZIP-1251497
