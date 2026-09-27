# [H] Directory Traversal in list-n-stream

## Summary
Severity: High
Advisory: GHSA-23vf-5g53-hm9q
CVE: CVE-2017-16084
CWE: CWE-22
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-23vf-5g53-hm9q
Type: github-advisory

## Affected
- npm: `list-n-stream` — affected >=0 <0.0.11

## Details
Affected versions of `list-n-stream` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

Update to version 0.0.11 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16084
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/list-n-stream
- https://github.com/advisories/GHSA-23vf-5g53-hm9q
- https://www.npmjs.com/advisories/344
