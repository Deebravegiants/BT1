# [C] X-Forwarded-For header allows brute-forcing autoblocked IP addresses

## Summary
Severity: Critical
Advisory: GHSA-5vj8-g3qg-4qh6
CVE: CVE-2023-29141
CWE: CWE-444
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-5vj8-g3qg-4qh6
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.39.0 <1.39.3
- Packagist: `mediawiki/core` — affected >=1.38.0 <1.38.6
- Packagist: `mediawiki/core` — affected >=0 <1.35.10

## Details
An issue was discovered in MediaWiki before 1.35.10, 1.36.x through 1.38.x before 1.38.6, and 1.39.x before 1.39.3. An auto-block can occur for an untrusted X-Forwarded-For header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29141
- https://gerrit.wikimedia.org/r/plugins/gitiles/mediawiki/core/+/REL1_39/RELEASE-NOTES-1.39
- https://github.com/wikimedia/mediawiki
- https://lists.debian.org/debian-lts-announce/2023/08/msg00029.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ONWHGOBFD6CQAEGOP5O375XAP2N6RUHT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZGK4NZPIJ5ET2ANRZOUYPCRIB5I64JR7
- https://phabricator.wikimedia.org/T285159
- https://www.debian.org/security/2023/dsa-5447
- https://www.mediawiki.org/wiki/Release_notes/1.35#MediaWiki_1.35.10
- https://www.mediawiki.org/wiki/Release_notes/1.38#MediaWiki_1.38.6
- https://www.mediawiki.org/wiki/Release_notes/1.39#MediaWiki_1.39.3
