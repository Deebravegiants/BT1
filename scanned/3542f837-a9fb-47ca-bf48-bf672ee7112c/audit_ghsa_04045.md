# [H] Directory Traversal in ltt.js

## Summary
Severity: High
Advisory: GHSA-6qh5-wx38-q92g
CWE: CWE-22
Ecosystem: npm
Published: 2019-05-30
Source: https://github.com/advisories/GHSA-6qh5-wx38-q92g
Type: github-advisory

## Affected
- npm: `ltt.js` — affected 1.0.0

## Details
Affected versions of `ltt.js` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

Example request:
```
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/ltt.js
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/ltt.js
- https://www.npmjs.com/advisories/411
