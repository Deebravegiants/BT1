# [H] Cross-Site Scripting in highcharts

## Summary
Severity: High
Advisory: GHSA-gr4j-r575-g665
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-08-25
Source: https://github.com/advisories/GHSA-gr4j-r575-g665
Type: github-advisory

## Affected
- npm: `highcharts` — affected >=0 <7.2.2
- npm: `highcharts` — affected >=8.0.0 <8.1.1

## Details
Versions of `highcharts` prior to 7.2.2 or 8.1.1 are vulnerable to Cross-Site Scripting (XSS).  The package fails to sanitize `href` values and does not restrict URL schemes, allowing attackers to execute arbitrary JavaScript in a victim's browser if they click the link.

## References
- https://github.com/highcharts/highcharts/issues/13559
- https://github.com/highcharts/highcharts/commit/55c39dd55f12ce8dfab84f8ec13ad81423bee9f5
- https://github.com/highcharts/highcharts
- https://snyk.io/vuln/SNYK-JS-HIGHCHARTS-571995
