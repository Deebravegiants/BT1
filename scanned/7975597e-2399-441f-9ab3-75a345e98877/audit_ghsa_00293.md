# [H] Directory Traversal in node-simple-router

## Summary
Severity: High
Advisory: GHSA-5w8q-x7hc-jhp6
CVE: CVE-2017-16083
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-5w8q-x7hc-jhp6
Type: github-advisory

## Affected
- npm: `node-simple-router` — affected >=0 <0.10.1

## Details
Affected versions of `node-simple-router` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

Update to v0.10.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16083
- https://github.com/sandy98/node-simple-router/commit/dfdd52e2e80607af433097d940b3834fd96df488
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/node-simple-router
- https://github.com/advisories/GHSA-5w8q-x7hc-jhp6
- https://www.npmjs.com/advisories/352
