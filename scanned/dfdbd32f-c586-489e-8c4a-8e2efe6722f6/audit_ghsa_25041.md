# [H] Typo3 Vulnerable to Cache Poisoning

## Summary
Severity: High
Advisory: GHSA-5479-gqqr-f9gj
CVE: CVE-2014-9509
CWE: CWE-20
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5479-gqqr-f9gj
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.39
- Packagist: `typo3/cms` — affected >=6.2.0 <6.2.9
- Packagist: `typo3/cms` — affected >=7.0.0 <7.0.2
- Packagist: `typo3/cms` — affected >=4.6.0 <4.6.19
- Packagist: `typo3/cms` — affected >=4.7.0 <4.7.21
- Packagist: `typo3/cms` — affected >=6.0.0 <6.0.15
- Packagist: `typo3/cms` — affected >=6.1.0 <6.1.13

## Details
**Problem Description:** A request URL with arbitrary arguments, but still pointing to the home page of  a TYPO3 installation can be cached if the configuration option `config.prefixLocalAnchors` is used with the values "all" or "cached". The impact of this vulnerability is that unfamiliar looking links to the home page can end up in the cache, which leads to a reload of the page in the browser when section links are followed by web page visitors, instead of just directly jumping to the requested section of the page. TYPO3 versions 4.6.x and higher are only affected if the homepage is not a shortcut to a different page.

**Solution:** Removing the configuration options `config.prefixLocalAnchors` (and optionally also config.baseUrl) in favor of `config.absRefPrefix`

**Credits:** Thanks to Gernot Leitgab who discovered and reported the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9509
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2014-003
