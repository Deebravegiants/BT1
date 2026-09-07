# [H] Directory Traversal in sencisho

## Summary
Severity: High
Advisory: GHSA-6866-x7cf-rmh5
CVE: CVE-2017-16092
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-6866-x7cf-rmh5
Type: github-advisory

## Affected
- npm: `sencisho` — affected >=0

## Details
Affected versions of `sencisho` are vulnerable to a directory traversal issue, giving an attacker access to the filesystem by placing "../" in the URL.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16092
- https://github.com/JacksonGL/NPM-Vuln-PoC/tree/master/directory-traversal/sencisho
- https://github.com/advisories/GHSA-6866-x7cf-rmh5
- https://www.npmjs.com/advisories/340
