# [H] Prototype pollution in chart.js

## Summary
Severity: High
Advisory: GHSA-h68q-55jf-x68w
CVE: CVE-2020-7746
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-h68q-55jf-x68w
Type: github-advisory

## Affected
- npm: `chart.js` — affected >=0 <2.9.4

## Details
This affects the package chart.js before 2.9.4. The options parameter is not properly sanitized when it is processed. When the options are processed, the existing options (or the defaults options) are deeply merged with provided options. However, during this operation, the keys of the object being set are not checked, leading to a prototype pollution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7746
- https://github.com/chartjs/Chart.js/pull/7920
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1019375
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBCHARTJS-1019376
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1019374
- https://snyk.io/vuln/SNYK-JS-CHARTJS-1018716
