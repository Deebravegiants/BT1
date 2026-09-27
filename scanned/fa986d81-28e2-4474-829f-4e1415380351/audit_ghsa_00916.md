# [H] Directory Traversal in nodeload-nmickuli

## Summary
Severity: High
Advisory: GHSA-wmcq-3wfx-qjx5
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-wmcq-3wfx-qjx5
Type: github-advisory

## Affected
- npm: `nodeload-nmickuli` — affected >=0.0.0

## Details
Affected versions of `nodeload-nmickuli` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

Example request:
```
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/nodeload-nmickuli
- https://www.npmjs.com/advisories/410
