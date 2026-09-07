# [H] Wikimedia Potential DOS due to slow WatchedItemStore::countVisitingWatchersMultiple

## Summary
Severity: High
Advisory: GHSA-33xw-x3pr-rvqj
CVE: CVE-2019-12473
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-33xw-x3pr-rvqj
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=1.27.0 <1.27.6
- Packagist: `mediawiki/core` — affected >=1.30.0 <1.30.2
- Packagist: `mediawiki/core` — affected >=1.31.0 <1.31.2
- Packagist: `mediawiki/core` — affected >=1.32.0 <1.32.2

## Details
Wikimedia MediaWiki 1.27.0 through 1.32.1 might allow DoS. Passing invalid titles to the API could cause a DoS by querying the entire watchlist table. Fixed in 1.32.2, 1.31.2, 1.30.2 and 1.27.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12473
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2019-12473.yaml
- https://github.com/wikimedia/mediawiki
- https://lists.wikimedia.org/pipermail/wikitech-l/2019-June/092152.html
- https://phabricator.wikimedia.org/T204729
- https://seclists.org/bugtraq/2019/Jun/12
- https://www.debian.org/security/2019/dsa-4460
