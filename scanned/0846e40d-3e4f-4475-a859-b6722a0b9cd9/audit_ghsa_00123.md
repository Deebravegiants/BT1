# [M] Directory Traversal in elding

## Summary
Severity: Medium
Advisory: GHSA-rp28-29ch-gh92
CVE: CVE-2017-16222
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-08-06
Source: https://github.com/advisories/GHSA-rp28-29ch-gh92
Type: github-advisory

## Affected
- npm: `elding` — affected >=0

## Details
Affected versions of `elding` resolve relative file paths, resulting in a directory traversal vulnerability. A malicious actor can use this vulnerability to access files outside of the intended directory root, which may result in the disclosure of private files on the vulnerable system.

This vulnerability only affects files that have file extensions - i.e. `/etc/passwd` will be treated as a directory, and a read attempt on `/etc/passwd/index.js` will be made and subsequently fail. 

**Example request:**
```http
GET /../../../../../../../../../../some_app_dir/secrets.json HTTP/1.1
host:foo
```


## Recommendation

No patch is available for this vulnerability.

It is recommended that the package is only used for local development, and if the functionality is needed for production, a different package is used instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16222
- https://github.com/JacksonGL/NPM-Vuln-PoC/blob/master/directory-traversal/elding
- https://github.com/advisories/GHSA-rp28-29ch-gh92
- https://www.npmjs.com/advisories/415
