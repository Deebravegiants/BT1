# [M] MediaWiki Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mqhw-wq8p-vf5r
CVE: CVE-2020-10959
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mqhw-wq8p-vf5r
Type: github-advisory

## Affected
- Packagist: `mediawiki/core` — affected >=0 <1.34.0-rc.0

## Details
resources/src/mediawiki.page.ready/ready.js in MediaWiki before 1.34.0-rc.0 allows remote attackers to force a logout and external redirection via HTML content in a MediaWiki page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10959
- https://github.com/wikimedia/mediawiki/commit/d4a552e65bdfd7309a9b8537e9dbe69c5e2991eb
- https://gerrit.wikimedia.org/r/c/mediawiki/core/+/536725
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mediawiki/core/CVE-2020-10959.yaml
- https://github.com/wikimedia/mediawiki
- https://phabricator.wikimedia.org/T232932
- https://phabricator.wikimedia.org/T240393
