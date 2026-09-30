# [H] Inefficient Regular Expression Complexity in handsontable

## Summary
Severity: High
Advisory: GHSA-hf66-r44g-p7j9
CVE: CVE-2021-23446
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-30
Source: https://github.com/advisories/GHSA-hf66-r44g-p7j9
Type: github-advisory

## Affected
- npm: `handsontable` — affected >=0 <10.0.0

## Details
The package handsontable from 0 and before 10.0.0 are vulnerable to Regular Expression Denial of Service (ReDoS) in `Handsontable.helper.isNumeric` function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23446
- https://github.com/handsontable/handsontable/issues/8752
- https://github.com/handsontable/handsontable/pull/8742
- https://github.com/handsontable/handsontable
- https://snyk.io/vuln/SNYK-DOTNET-HANDSONTABLE-1726793
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1726795
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1726796
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBHANDSONTABLE-1726794
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1726797
- https://snyk.io/vuln/SNYK-JS-HANDSONTABLE-1726770
