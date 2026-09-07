# [M] Wikimedia MediaWik exposed suppressed log in RevisionDelete page

## Summary
Severity: Medium
Advisory: GHSA-733q-m38x-q7cc
CVE: CVE-2019-12470
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-733q-m38x-q7cc
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.27.0 <1.27.6
- Packagist: `mediawiki/core` — affected >=1.30.0 <1.30.2
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.2
- Packagist: `mediawiki/core` — affected >=1.32.0 <1.32.2

## Details
Wikimedia MediaWiki through 1.32.1 has Incorrect Access Control. Suppressed log in RevisionDelete page is exposed. Fixed in 1.32.2, 1.31.2, 1.30.2 and 1.27.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12470
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2019-12470.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.wikimedia.org/pipermail/wikitech-l/2019-June/092152.html
- https://phabricator.wikimedia.org/T222038
- https://seclists.org/bugtraq/2019/Jun/12
- https://www.debian.org/security/2019/dsa-4460
