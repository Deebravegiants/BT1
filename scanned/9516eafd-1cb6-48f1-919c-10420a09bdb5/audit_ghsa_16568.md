# [H] TYPO3 possible cache poisoning on the homepage when anchors are used

## Summary
Severity: High
Advisory: GHSA-p84g-j2gh-83g3
Ecosystem: Packagist
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-p84g-j2gh-83g3
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.9
- Packagist: `typo3/cms` — affected >=7.0.0 <7.0.2

## Details
A request URL with arbitrary arguments, but still pointing to the home page of  a TYPO3 installation can be cached if the configuration option config.prefixLocalAnchors is used with the values "all" or "cached". The impact of this vulnerability is that unfamiliar looking links to the home page can end up in the cache, which leads to a reload of the page in the browser when section links are followed by web page visitors, instead of just directly jumping to the requested section of the page. TYPO3 versions 4.6.x and higher are only affected if the homepage is not a shortcut to a different page.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2014-12-09-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2014-003
