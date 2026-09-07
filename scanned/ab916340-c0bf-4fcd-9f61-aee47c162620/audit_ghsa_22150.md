# [M] SabreDAV Directory Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qg5v-jw6f-rpfj
CVE: CVE-2013-1939
CWE: CWE-20, CWE-22
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qg5v-jw6f-rpfj
Type: github-advisory

## Affected
- Packagist: `sabre/dav` — affected >=1.7.0 <1.7.7
- Packagist: `sabre/dav` — affected >=1.8.0 <1.8.5
- Packagist: `sabre/dav` — affected >=1.6.0 <1.6.9

## Details
The HTML\Browser plugin in SabreDAV before 1.6.9, 1.7.x before 1.7.7, and 1.8.x before 1.8.5, as used in ownCloud, when running on Windows, does not properly check path separators in the base path, which allows remote attackers to read arbitrary files via a `\` (backslash) character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1939
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sabre/dav/CVE-2013-1939.yaml
- https://github.com/sabre-io/dav
- https://groups.google.com/forum/?fromgroups=#!topic/sabredav-discuss/ehOUu7wTSGQ
- https://groups.google.com/forum/?fromgroups=#%21topic/sabredav-discuss/ehOUu7wTSGQ
- http://owncloud.org/about/security/advisories/oC-SA-2013-016
