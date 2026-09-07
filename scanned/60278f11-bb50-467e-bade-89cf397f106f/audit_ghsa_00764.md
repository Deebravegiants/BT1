# [M] Cross-Site Scripting in node-red

## Summary
Severity: Medium
Advisory: GHSA-8w65-xjc5-9w79
CVE: CVE-2019-15607
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-01-30
Source: https://github.com/advisories/GHSA-8w65-xjc5-9w79
Type: github-advisory

## Affected
- npm: `node-red` — affected >=0 <0.20.8

## Details
Versions of `node-red` prior to 0.20.8are vulnerable to Cross-Site Scripting (XSS). The package fails to sanitize the `name` field in new Flows, allowing attackers to execute arbitrary JavaScript in the victim's browser.


## Recommendation

Upgrade to version 0.18.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15607
- https://hackerone.com/reports/681986
- https://www.npmjs.com/advisories/1456
