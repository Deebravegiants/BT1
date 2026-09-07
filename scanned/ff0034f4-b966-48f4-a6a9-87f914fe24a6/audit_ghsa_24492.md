# [M] Possible to circumvent title-blacklist

## Summary
Severity: Medium
Advisory: GHSA-pjv5-vv93-p648
CVE: CVE-2019-19709
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-pjv5-vv93-p648
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.6
- Packagist: `mediawiki/core` — affected >=1.32.0 <1.32.6
- Packagist: `mediawiki/core` — affected >=1.33.0 <1.33.2
- Packagist: `mediawiki/core` — affected >=1.33.99 <1.34.0

## Details
MediaWiki through 1.33.1 allows attackers to bypass the Title_blacklist protection mechanism by starting with an arbitrary title, establishing a non-resolvable redirect for the associated page, and using redirect=1 in the action API when editing that page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19709
- https://gerrit.wikimedia.org/r/q/Ie54f366986056c876eade0fcad6c41f70b8b8de8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2019-19709.yaml
- https://github.com/wikimedia/mediawiki
- https://phabricator.wikimedia.org/T239466
- https://seclists.org/bugtraq/2019/Dec/48
- https://www.debian.org/security/2019/dsa-4592
