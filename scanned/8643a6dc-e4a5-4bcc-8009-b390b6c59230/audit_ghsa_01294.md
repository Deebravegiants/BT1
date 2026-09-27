# [M] Directory Traversal in featurebook

## Summary
Severity: Medium
Advisory: GHSA-7x92-2j68-h32c
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-7x92-2j68-h32c
Type: github-advisory

## Affected
- npm: `featurebook` — affected >=0

## Details
Affected versions of `featurebook` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

The `featurebook` package is not intended to be run in production code nor to be exposed to an untrusted network.


## Proof of Concept
```
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No direct patch is currently available.

At this time, the best mitigation is to ensure that `featurebook` is not running in production or exposed to an untrusted network.

## References
- https://hackerone.com/reports/296305
- https://www.npmjs.com/advisories/556
