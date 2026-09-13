# [H] Directory traversal in pooledwebsocket

## Summary
Severity: High
Advisory: GHSA-cfxm-4p54-5w7h
CVE: CVE-2017-16107
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-cfxm-4p54-5w7h
Type: github-advisory

## Affected
- npm: `pooledwebsocket` — affected >=0 <0.0.19

## Details
Affected versions of `pooledwebsocket` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

Update to version 0.0.19 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16107
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/pooledwebsocket
- https://github.com/advisories/GHSA-cfxm-4p54-5w7h
- https://www.npmjs.com/advisories/341
