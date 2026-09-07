# [M] Cross-site scripting in jspdf

## Summary
Severity: Medium
Advisory: GHSA-vh59-v9r5-4mh4
CVE: CVE-2020-7690
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-17
Source: https://github.com/advisories/GHSA-vh59-v9r5-4mh4
Type: github-advisory

## Affected
- npm: `jspdf` — affected >=0 <2.0.0

## Details
Affected versions of this package are vulnerable to Cross-site Scripting (XSS). It's possible to inject JavaScript code via the `html` method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7690
- https://github.com/MrRio/jsPDF/issues/2795
- https://github.com/parallax/jsPDF/issues/2862
- https://github.com/parallax/jsPDF/issues/2971
- https://github.com/parallax/jsPDF/pull/2806
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-575260
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-575258
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBMRRIO-575259
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-575257
- https://snyk.io/vuln/SNYK-JS-JSPDF-575256
