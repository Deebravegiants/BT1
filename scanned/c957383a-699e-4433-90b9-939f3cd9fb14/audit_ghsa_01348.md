# [H] Cross-Site Scripting in buefy

## Summary
Severity: High
Advisory: GHSA-xwqw-rf2q-xmhf
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-xwqw-rf2q-xmhf
Type: github-advisory

## Affected
- npm: `buefy` — affected >=0 <0.7.2

## Details
Versions of buefy prior to 0.7.2 are vulnerable to Cross-Site Scripting, allowing attackers to manipulate the DOM and execute remote code. The autocomplete list renders user input as HTML without encoding.


## Recommendation

Upgrade to version 0.7.2 or later.

## References
- https://github.com/buefy/buefy/issues/1097
- https://github.com/buefy/buefy
- https://www.npmjs.com/advisories/747
