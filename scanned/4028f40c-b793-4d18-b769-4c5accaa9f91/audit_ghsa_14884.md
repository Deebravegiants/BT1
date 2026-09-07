# [M] Cache Flooding in TYPO3 Frontend

## Summary
Severity: Medium
Advisory: GHSA-pw2q-qwvj-gh43
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-pw2q-qwvj-gh43
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.27
- Packagist: `typo3/cms` — affected >=7.6.0 <7.6.11
- Packagist: `typo3/cms` — affected >=8.0.0 <8.3.1

## Details
Links with a valid cHash argument lead to newly generated page cache entries. Because the cHash is not bound to a specific page, attackers could use valid cHash arguments for multiple pages, leading to additional useless page cache entries. Depending on the number of pages in the system and the number of available valid links with a cHash, attackers could add a considerable amount of additional cache entries, which in the end exceed storage limits and thus could lead to the system not responding any more. This means the Cache Flooding attack potentially could lead to a successful Denial of Service (DoS) attack.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2016-09-14-2.yaml
