# [C] Cross-site Scripting (XSS) in Eclipse Theia

## Summary
Severity: Critical
Advisory: GHSA-gcm9-cc3r-c6vj
CVE: CVE-2020-27224
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-gcm9-cc3r-c6vj
Type: github-advisory

## Affected
- npm: `@theia/preview` — affected >=0 <1.3.0

## Details
In Eclipse Theia versions up to and including 1.2.0, the Markdown Preview (@theia/preview), can be exploited to execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-27224
- https://github.com/eclipse-theia/theia/issues/7954
- https://github.com/eclipse-theia/theia/pull/7971
- https://omespino.com/write-up-google-bug-bounty-xss-to-cloud-shell-instance-takeover-rce-as-root-5000-usd
