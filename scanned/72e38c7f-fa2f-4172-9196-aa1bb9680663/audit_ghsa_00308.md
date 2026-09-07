# [H] Directory Traversal in iter-http

## Summary
Severity: High
Advisory: GHSA-3cgg-gh9j-w8vm
CVE: CVE-2017-16094
CWE: CWE-22
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-3cgg-gh9j-w8vm
Type: github-advisory

## Affected
- npm: `iter-http` — affected >=0

## Details
Affected versions of `iter-http` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16094
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/iter-http
- https://github.com/advisories/GHSA-3cgg-gh9j-w8vm
- https://www.npmjs.com/advisories/343
