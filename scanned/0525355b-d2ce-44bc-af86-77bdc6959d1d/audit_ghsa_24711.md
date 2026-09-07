# [H] OATHAuth extension in MediaWiki is not implementing rate limit

## Summary
Severity: High
Advisory: GHSA-rqvj-fc2x-99q6
CVE: CVE-2020-25827
CWE: CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rqvj-fc2x-99q6
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.9
- Packagist: `mediawiki/core` — affected >=1.32.0 <1.34.3

## Details
An issue was discovered in the OATHAuth extension in MediaWiki before 1.31.9 and 1.32.x through 1.34.x before 1.34.3. For Wikis using OATHAuth on a farm/cluster (such as via CentralAuth), rate limiting of OATH tokens is only done on a single site level. Thus, multiple requests can be made across many wikis/sites concurrently.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25827
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2020-25827.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RTTPZ7XMDS66I442OLLHXBDNP2LCBJU6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RTTPZ7XMDS66I442OLLHXBDNP2LCBJU6
- https://lists.wikimedia.org/pipermail/mediawiki-l/2020-September/048480.html
- https://lists.wikimedia.org/pipermail/mediawiki-l/2020-September/048488.html
- https://phabricator.wikimedia.org/T251661
