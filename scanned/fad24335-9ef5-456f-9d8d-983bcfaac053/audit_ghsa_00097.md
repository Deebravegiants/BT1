# [M] metascraper before v5.2.0 vulnerable to stored cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-8f64-q7jc-ccgp
CVE: CVE-2018-3773
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-08-08
Source: https://github.com/advisories/GHSA-8f64-q7jc-ccgp
Type: github-advisory

## Affected
- npm: `metascraper` — affected >=0 <5.2.0

## Details
Versions of `metascraper` prior to 5.2.0 are vulnerable to stored cross-site scripting (XSS).


## Recommendation

Upgrade to version 5.2.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3773
- https://github.com/microlinkhq/metascraper/pull/169
- https://hackerone.com/reports/309367
- https://github.com/microlinkhq/metascraper
- https://www.npmjs.com/advisories/603
