# [H] Directory Traversal in yjmyjmyjm

## Summary
Severity: High
Advisory: GHSA-g376-whg7-896m
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-g376-whg7-896m
Type: github-advisory

## Affected
- npm: `yjmyjmyjm` — affected >=0.0.0

## Details
Affected versions of `yjmyjmyjm` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

Example request:
```
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/yjmyjmyjm
- https://www.npmjs.com/advisories/451
