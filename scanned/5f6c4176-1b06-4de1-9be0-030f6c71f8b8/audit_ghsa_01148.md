# [H] Directory Traversal in qinserve

## Summary
Severity: High
Advisory: GHSA-cxwc-8pqp-2whw
CVE: CVE-2017-16197
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-cxwc-8pqp-2whw
Type: github-advisory

## Affected
- npm: `qinserve` — affected >=0.0.0

## Details
Affected versions of `qinserve` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16197
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/qinserve
- https://www.npmjs.com/advisories/434
