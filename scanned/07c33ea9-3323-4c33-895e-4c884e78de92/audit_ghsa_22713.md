# [H] MediaWiki Incorrect Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-7mqg-5fgh-xh4r
CVE: CVE-2019-12472
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7mqg-5fgh-xh4r
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.18.0 <1.27.6
- Packagist: `mediawiki/core` — affected >=1.30.0 <1.30.2
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.2
- Packagist: `mediawiki/core` — affected >=1.32.0 <1.32.2

## Details
An Incorrect Access Control vulnerability was found in Wikimedia MediaWiki 1.18.0 through 1.32.1. It is possible to bypass the limits on IP range blocks ($wgBlockCIDRLimit) by using the API. Fixed in 1.32.2, 1.31.2, 1.30.2 and 1.27.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12472
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2019-12472.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.wikimedia.org/pipermail/wikitech-l/2019-June/092152.html
- https://phabricator.wikimedia.org/T199540
