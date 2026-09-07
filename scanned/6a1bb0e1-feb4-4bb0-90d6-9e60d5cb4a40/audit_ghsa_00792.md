# [H] Directory Traversal in fancy-server

## Summary
Severity: High
Advisory: GHSA-m273-wwfv-h6jp
CVE: CVE-2014-10066
CWE: CWE-22
Ecosystem: npm
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-m273-wwfv-h6jp
Type: github-advisory

## Affected
- npm: `fancy-server` — affected >=0 <0.1.4

## Details
Versions 0.1.4 and earlier of fancy-server are vulnerable to a directory traversal attack. 

Standard attack vectors such as `../` will allow an attacker to read files outside of the served directory.


## Recommendation

Upgrade to version 0.1.4 or greater.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-10066
- https://www.npmjs.com/advisories/9
- http://en.wikipedia.org/wiki/Directory_traversal_attack
