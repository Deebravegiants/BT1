# [M] MediaWiki information disclosure

## Summary
Severity: Medium
Advisory: GHSA-7hwr-f745-5rwq
CVE: CVE-2019-16738
CWE: CWE-200, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7hwr-f745-5rwq
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.4
- Packagist: `mediawiki/core` — affected >=1.32.0 <1.32.4
- Packagist: `mediawiki/core` — affected >=1.33.0 <1.33.1

## Details
In MediaWiki through 1.33.0, Special:Redirect allows information disclosure of suppressed usernames via a User ID Lookup.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16738
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2019-16738.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7OMG3BMUHGWTAPYTK2NXM6CXF6FYLOUO
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QBAOLXETM5BOYQG6OQVHGB2LNLZUXVN6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7OMG3BMUHGWTAPYTK2NXM6CXF6FYLOUO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QBAOLXETM5BOYQG6OQVHGB2LNLZUXVN6
- https://phabricator.wikimedia.org/T230402
- https://seclists.org/bugtraq/2019/Oct/32
- https://www.debian.org/security/2019/dsa-4545
