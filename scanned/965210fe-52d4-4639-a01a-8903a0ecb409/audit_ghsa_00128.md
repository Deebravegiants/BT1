# [H] js-bson vulnerable to REDoS

## Summary
Severity: High
Advisory: GHSA-8462-q7x7-g2x4
CVE: CVE-2018-13863
CWE: CWE-185, CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-09-17
Source: https://github.com/advisories/GHSA-8462-q7x7-g2x4
Type: github-advisory

## Affected
- npm: `bson` — affected >=0.5.0 <1.0.5

## Details
The MongoDB bson JavaScript module (also known as js-bson) versions 0.5.0 to 1.0.x before 1.0.5 is vulnerable to a Regular Expression Denial of Service (ReDoS) in lib/bson/decimal128.js. The flaw is triggered when the Decimal128.fromString() function is called to parse a long untrusted string.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13863
- https://github.com/mongodb/js-bson/commit/bd61c45157c53a1698ff23770160cf4783e9ea4a
- https://github.com/advisories/GHSA-8462-q7x7-g2x4
- https://github.com/mongodb/js-bson
- https://snyk.io/vuln/npm:bson:20180225
