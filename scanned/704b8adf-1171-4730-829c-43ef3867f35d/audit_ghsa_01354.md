# [H] Directory Traversal in wenluhong1

## Summary
Severity: High
Advisory: GHSA-224h-p7p5-rh85
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-224h-p7p5-rh85
Type: github-advisory

## Affected
- npm: `wenluhong1` — affected >=0.0.0

## Details
Affected versions of `wenluhong1` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

Example request:
```
GET /../../../../../../../../../../etc/passwd HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/wenluhong1
- https://snyk.io/vuln/npm:wenluhong1:20170509
- https://www.npmjs.com/advisories/409
