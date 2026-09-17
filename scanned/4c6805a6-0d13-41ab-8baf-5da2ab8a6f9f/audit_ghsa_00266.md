# [H] Directory Traversal in tinyserver2

## Summary
Severity: High
Advisory: GHSA-g8wf-rcg3-qw4q
CVE: CVE-2017-16085
CWE: CWE-22
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-g8wf-rcg3-qw4q
Type: github-advisory

## Affected
- npm: `tinyserver2` — affected >=0 <0.6.0

## Details
Affected versions of `tinyserver2` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

Update to v0.6.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16085
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/tinyserver2
- https://github.com/advisories/GHSA-g8wf-rcg3-qw4q
- https://www.npmjs.com/advisories/371
