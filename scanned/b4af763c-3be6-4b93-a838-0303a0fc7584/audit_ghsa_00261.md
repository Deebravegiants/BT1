# [M] Remote Code Execution in markdown-pdf

## Summary
Severity: Medium
Advisory: GHSA-p7c9-jqhq-vr3v
CVE: CVE-2018-3770
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-27
Source: https://github.com/advisories/GHSA-p7c9-jqhq-vr3v
Type: github-advisory

## Affected
- npm: `markdown-pdf` — affected >=0 <9.0.0

## Details
Versions of `markdown-pdf` prior to 9.0.0 are vulnerable to Remote Code Execution. The package fails to sanitize HTML code in markdown files. If markdown files with malicious HTML are converted to PDF, the resulting PDF file will execute any JavaScript code in the original markdown file. This may allow attackers to execute Remote Code.


## Recommendation

Upgrade to version 9.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3770
- https://hackerone.com/reports/360727
- https://github.com/advisories/GHSA-p7c9-jqhq-vr3v
- https://www.npmjs.com/advisories/991
