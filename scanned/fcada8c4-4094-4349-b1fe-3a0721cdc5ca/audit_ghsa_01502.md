# [H] Directory Traversal in jansenstuffpleasework

## Summary
Severity: High
Advisory: GHSA-f8rj-4v7g-p5rj
CVE: CVE-2017-16176
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-f8rj-4v7g-p5rj
Type: github-advisory

## Affected
- npm: `jansenstuffpleasework` — affected >=0.0.0

## Details
Affected versions of `jansenstuffpleasework` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

**Example request:**
```http
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16176
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/jansenstuffpleasework
- https://www.npmjs.com/advisories/464
