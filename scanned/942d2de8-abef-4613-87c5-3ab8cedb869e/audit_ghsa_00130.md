# [M] Cross-Site Scripting in glance

## Summary
Severity: Medium
Advisory: GHSA-7375-vjr2-3g7w
CVE: CVE-2018-3748
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-09-27
Source: https://github.com/advisories/GHSA-7375-vjr2-3g7w
Type: github-advisory

## Affected
- npm: `glance` — affected >=0 <3.0.8

## Details
Versions of `glance` before 3.0.8 are vulnerable to Stored Cross-Site Scripting (XSS). This is only exploitable if the attacker is able to control the name of a file that is served by the `glance` package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3748
- https://github.com/jarofghosts/glance/commit/cdc68bb68d785343ddb829f1adc130cdd6169533
- https://hackerone.com/reports/310133
- https://github.com/advisories/GHSA-7375-vjr2-3g7w
- https://github.com/jarofghosts/glance
- https://www.npmjs.com/advisories/610
