# [M] Multiple Content Injection Vulnerabilities in marked

## Summary
Severity: Medium
Advisory: GHSA-9cw2-jqp5-7x39
CVE: CVE-2014-3743
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-9cw2-jqp5-7x39
Type: github-advisory

## Affected
- npm: `marked` — affected >=0 <0.3.1

## Details
Versions 0.3.0 and earlier of `marked` are affected by two cross-site scripting vulnerabilities, even when `sanitize: true` is set.

The attack vectors for this vulnerability are GFM Codeblocks and JavaScript URLs.


## Recommendation

Upgrade to version 0.3.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-1850
- https://www.npmjs.com/advisories/22
