# [H] Directory Traversal in chatbyvista

## Summary
Severity: High
Advisory: GHSA-8w74-g84v-c5w8
CVE: CVE-2017-16177
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-8w74-g84v-c5w8
Type: github-advisory

## Affected
- npm: `chatbyvista` — affected >=0.0.0

## Details
Affected versions of `chatbyvista` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16177
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/chatbyvista
- https://www.npmjs.com/advisories/462
