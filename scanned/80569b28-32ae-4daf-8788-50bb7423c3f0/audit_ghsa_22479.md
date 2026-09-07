# [M] Mediawiki tarball is missing .htaccess files

## Summary
Severity: Medium
Advisory: GHSA-2c28-7gwv-cpgf
CVE: CVE-2018-13258
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2c28-7gwv-cpgf
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.1

## Details
Mediawiki 1.31 before 1.31.1 misses .htaccess files in the provided tarball used to protect some directories that shouldn't be web accessible.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-13258
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2018-13258.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.wikimedia.org/pipermail/wikitech-l/2018-September/090849.html
- https://phabricator.wikimedia.org/T199029
- http://www.securitytracker.com/id/1041695
