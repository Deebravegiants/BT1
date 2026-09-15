# [M] Converse.js Exposure of Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-mv4h-qm24-x4gh
CVE: CVE-2018-6591
CWE: CWE-200
Ecosystem: Packagist, npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mv4h-qm24-x4gh
Type: github-advisory

## Affected
- Packagist: `jcbrand/converse.js` — affected >=0 <3.3.3
- npm: `converse.js` — affected >=0 <3.3.3

## Details
Converse.js and Inverse.js through 3.3 allow remote attackers to obtain sensitive information because it is too difficult to determine whether safe publication of private data was configured or even intended. For example, users might have an expectation that chatroom bookmarks are private, but the various interacting software components do not necessarily make that happen.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6591
- https://github.com/conversejs/converse.js/commit/ba09996998df38a5eb76903457fbb1077caabe25
- https://github.com/conversejs/converse.js
- https://gultsch.de/converse_bookmarks.html
