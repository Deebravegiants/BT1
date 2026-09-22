# [H] Directory Traversal in gaoxiaotingtingting

## Summary
Severity: High
Advisory: GHSA-qhf6-vqq9-q2p7
CVE: CVE-2017-16108
CWE: CWE-22
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-qhf6-vqq9-q2p7
Type: github-advisory

## Affected
- npm: `gaoxiaotingtingting` — affected >=0.0.0

## Details
Affected versions of `gaoxiaotingtingting` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16108
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/static-html-server
- https://www.npmjs.com/advisories/377
