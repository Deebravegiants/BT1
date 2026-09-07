# [M] TYPO3 ke_search XML External Entity Injection

## Summary
Severity: Medium
Advisory: GHSA-fq39-62gx-8hqx
CVE: CVE-2026-46722
CWE: CWE-611
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-fq39-62gx-8hqx
Type: github-advisory

## Affected
- Packagist: `tpwd/ke_search` — affected >=7.0.0 <7.0.1
- Packagist: `tpwd/ke_search` — affected >=6.0.0 <6.6.1
- Packagist: `tpwd/ke_search` — affected >=5.0.0 <5.6.2
- Packagist: `tpwd/ke_search` — affected >=0 <4.6.7

## Details
In TYPO3 faceted fulltext search (`ke_search`), the OOXML parsing of the file indexer does not disable external entity resolution. A crafted xlsx or pptx document placed in an indexed directory can cause local files to be read or outbound HTTP requests to be performed, with the retrieved content being written to the search index. This has been patched in versions 7.0.1, 6.6.1, 5.6.2 and 4.6.7.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46722
- https://github.com/FriendsOfPHP/security-advisories/blob/master/tpwd/ke_search/CVE-2026-46722.yaml
- https://github.com/tpwd/ke_search
- https://typo3.org/security/advisory/typo3-ext-sa-2026-011
