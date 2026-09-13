# [H] Directory Traversal in node-server-forfront

## Summary
Severity: High
Advisory: GHSA-j38m-7q52-fgfh
CVE: CVE-2017-16124
CWE: CWE-22
Ecosystem: npm
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-j38m-7q52-fgfh
Type: github-advisory

## Affected
- npm: `node-server-forfront` — affected >=0

## Details
Affected versions of `node-server-forfront` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16124
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/node-server-forfront
- https://github.com/advisories/GHSA-j38m-7q52-fgfh
- https://www.npmjs.com/advisories/382
