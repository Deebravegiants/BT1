# [M] Header injection in nodemailer

## Summary
Severity: Medium
Advisory: GHSA-hwqf-gcqm-7353
CVE: CVE-2021-23400
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-12-10
Source: https://github.com/advisories/GHSA-hwqf-gcqm-7353
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=0 <6.6.1

## Details
The package nodemailer before 6.6.1 are vulnerable to HTTP Header Injection if unsanitized user input that may contain newlines and carriage returns is passed into an address object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23400
- https://github.com/nodemailer/nodemailer/issues/1289
- https://github.com/nodemailer/nodemailer/commit/7e02648cc8cd863f5085bad3cd09087bccf84b9f
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1314737
- https://snyk.io/vuln/SNYK-JS-NODEMAILER-1296415
