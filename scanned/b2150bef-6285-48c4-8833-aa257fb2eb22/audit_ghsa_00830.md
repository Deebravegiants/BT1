# [H] Directory Traversal in wffserve

## Summary
Severity: High
Advisory: GHSA-wqr3-24xm-fxhq
CVE: CVE-2017-16168
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-wqr3-24xm-fxhq
Type: github-advisory

## Affected
- npm: `wffserve` — affected >=0.0.0

## Details
Affected versions of `wffserve` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16168
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/city-weather-abe
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/wffserve
- https://www.npmjs.com/advisories/407
