# [M] Mediawiki Improper Privilege Management

## Summary
Severity: Medium
Advisory: GHSA-mhfv-9h99-jwg7
CVE: CVE-2018-0503
CWE: CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mhfv-9h99-jwg7
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.27.0 <1.27.5
- Packagist: `mediawiki/core` — affected >=1.29.0 <1.29.3
- Packagist: `mediawiki/core` — affected >=1.30.0 <1.30.1
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.1

## Details
Mediawiki 1.31 before 1.31.1, 1.30.1, 1.29.3 and 1.27.5 contains a flaw where contrary to the documentation, $wgRateLimits entry for 'user' overrides that for 'newbie'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-0503
- https://access.redhat.com/errata/RHSA-2019:3142
- https://access.redhat.com/errata/RHSA-2019:3238
- https://access.redhat.com/errata/RHSA-2019:3813
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2018-0503.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.wikimedia.org/pipermail/wikitech-l/2018-September/090849.html
- https://phabricator.wikimedia.org/T169545
- https://www.debian.org/security/2018/dsa-4301
- http://www.securitytracker.com/id/1041695
