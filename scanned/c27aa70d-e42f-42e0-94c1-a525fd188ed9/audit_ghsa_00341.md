# [M] No Charset in Content-Type Header in express

## Summary
Severity: Medium
Advisory: GHSA-gpvr-g6gh-9mc2
CVE: CVE-2014-6393
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-23
Source: https://github.com/advisories/GHSA-gpvr-g6gh-9mc2
Type: github-advisory

## Affected
- npm: `express` — affected >=0 <3.11.0
- npm: `express` — affected >=4.0.0 <4.5.0

## Details
Vulnerable versions of express do not specify a charset field in the content-type header while displaying 400 level response messages. The lack of enforcing user's browser to set correct charset, could be leveraged by an attacker to perform a cross-site scripting attack, using non-standard encodings, like UTF-7.


## Recommendation

For express 3.x, update express to version 3.11 or later.
For express 4.x, update express to version 4.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-6393
- https://bugzilla.redhat.com/show_bug.cgi?id=1203190
- https://github.com/advisories/GHSA-gpvr-g6gh-9mc2
- https://www.npmjs.com/advisories/8
