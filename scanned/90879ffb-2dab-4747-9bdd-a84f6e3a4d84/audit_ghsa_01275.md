# [H] Directory Traversal in zwserver

## Summary
Severity: High
Advisory: GHSA-whcm-29f4-j4mx
CVE: CVE-2017-16149
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-whcm-29f4-j4mx
Type: github-advisory

## Affected
- npm: `zwserver` — affected >=0.0.0

## Details
Affected versions of `zwserver` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16149
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/zwserver
- https://www.npmjs.com/advisories/372
