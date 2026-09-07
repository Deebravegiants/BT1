# [M] Cross-Site Scripting in html-janitor

## Summary
Severity: Medium
Advisory: GHSA-hfj4-96f7-6r5g
CVE: CVE-2017-0931
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-hfj4-96f7-6r5g
Type: github-advisory

## Affected
- npm: `html-janitor` — affected >=0 <2.0.3

## Details
Versions of `html-janitor` prior to 2.0.2 (all current versions) are vulnerable to cross-site scripting (XSS).

This is exploitable if user-controlled data is passed into the modules `clean()` function.


## Recommendation

No fix is currently available for this vulnerability. It is recommended to use an alternative module for HTML sanitization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0931
- https://github.com/guardian/html-janitor/issues/34
- https://hackerone.com/reports/308155
- https://github.com/advisories/GHSA-hfj4-96f7-6r5g
- https://www.npmjs.com/advisories/576
