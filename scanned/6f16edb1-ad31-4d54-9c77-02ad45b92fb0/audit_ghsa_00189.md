# [H] Directory Traversal in f2e-server

## Summary
Severity: High
Advisory: GHSA-g7j3-p357-cw8p
CVE: CVE-2017-16038
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-g7j3-p357-cw8p
Type: github-advisory

## Affected
- npm: `f2e-server` — affected >=0 <1.12.12

## Details
Affected versions of `f2e-server` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

Update to version 1.12.12 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16038
- https://github.com/shy2850/node-server/issues/10
- https://github.com/shy2850/node-server/pull/12/files
- https://github.com/advisories/GHSA-g7j3-p357-cw8p
- https://github.com/shy2850/node-server
- https://www.npmjs.com/advisories/346
