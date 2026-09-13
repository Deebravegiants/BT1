# [C] Command injection in nodemailer

## Summary
Severity: Critical
Advisory: GHSA-48ww-j4fc-435p
CVE: CVE-2020-7769
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-48ww-j4fc-435p
Type: github-advisory

## Affected
- npm: `nodemailer` — affected >=0 <6.4.16

## Details
This affects the package nodemailer before 6.4.16. Use of crafted recipient email addresses may result in arbitrary command flag injection in sendmail transport for sending mails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7769
- https://github.com/nodemailer/nodemailer/commit/ba31c64c910d884579875c52d57ac45acc47aa54
- https://github.com/nodemailer/nodemailer/blob/33b62e2ea6bc9215c99a9bb4bfba94e2fb27ebd0/lib/sendmail-transport/index.js#L75
- https://github.com/nodemailer/nodemailer/blob/33b62e2ea6bc9215c99a9bb4bfba94e2fb27ebd0/lib/sendmail-transport/index.js%23L75
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1039742
- https://snyk.io/vuln/SNYK-JS-NODEMAILER-1038834
- https://www.npmjs.com/package/nodemailer
