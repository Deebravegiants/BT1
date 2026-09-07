# [M] MediaWiki Special:UserRights exposes the existence of hidden users

## Summary
Severity: Medium
Advisory: GHSA-c4rj-wrmq-52rj
CVE: CVE-2020-25813
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c4rj-wrmq-52rj
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.9
- Packagist: `mediawiki/core` — affected >=1.32.0 <1.34.3

## Details
In MediaWiki before 1.31.9 and 1.32.x through 1.34.x before 1.34.3, Special:UserRights exposes the existence of hidden users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25813
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2020-25813.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RTTPZ7XMDS66I442OLLHXBDNP2LCBJU6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RTTPZ7XMDS66I442OLLHXBDNP2LCBJU6
- https://lists.wikimedia.org/pipermail/mediawiki-l/2020-September/048480.html
- https://lists.wikimedia.org/pipermail/mediawiki-l/2020-September/048488.html
- https://meta.wikimedia.org/wiki/Special:UserRights
- https://phabricator.wikimedia.org/T232568
