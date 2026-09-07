# [M] Typo3 Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-vccp-5v5h-p8m6
CVE: CVE-2014-3946
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vccp-5v5h-p8m6
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.3

## Details
Failing to respect user groups of logged in users when caching queries, Extbase is susceptible to information disclosure. The query caching (introduced in Extbase 6.2) used to cache queries that query results for a specific user group were presented to a different group.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3946
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2014-3946.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2014-001
- https://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2014-001
- http://www.debian.org/security/2014/dsa-2942
- http://www.openwall.com/lists/oss-security/2014/06/03/2
