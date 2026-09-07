# [M] Bypassing Sanitization using DOM clobbering in html-janitor

## Summary
Severity: Medium
Advisory: GHSA-fx46-whrj-73v5
CVE: CVE-2017-0928
CWE: CWE-547, CWE-642
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-fx46-whrj-73v5
Type: github-advisory

## Affected
- npm: `html-janitor` — affected >=0

## Details
All versions of `html-janitor` are vulnerable to cross-site scripting (XSS).

Arbitrary HTML can pass the sanitization process, which can be unexpected and dangerous (XSS) in case user-controlled input is passed to the clean function."


## Recommendation

Upgrade to version 2.0.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0928
- https://github.com/guardian/html-janitor/issues/35
- https://hackerone.com/reports/308158
- https://github.com/advisories/GHSA-fx46-whrj-73v5
- https://www.npmjs.com/advisories/569
