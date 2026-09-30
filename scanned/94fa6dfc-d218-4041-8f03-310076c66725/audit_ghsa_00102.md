# [M] Directory Traversal in jikes

## Summary
Severity: Medium
Advisory: GHSA-cpp2-q66x-fq44
CVE: CVE-2017-16139
CWE: CWE-22
Ecosystem: npm
Published: 2018-08-06
Source: https://github.com/advisories/GHSA-cpp2-q66x-fq44
Type: github-advisory

## Affected
- npm: `jikes` — affected 0.0.1

## Details
Affected versions of `jikes` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16139
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/jikes
- https://github.com/advisories/GHSA-cpp2-q66x-fq44
- https://www.npmjs.com/advisories/476
