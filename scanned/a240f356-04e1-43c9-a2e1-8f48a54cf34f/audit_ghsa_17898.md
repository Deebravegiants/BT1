# [M] Contao discloses sensitive information in the front end search index

## Summary
Severity: Medium
Advisory: GHSA-2xmj-8wmq-7475
CVE: CVE-2025-57756
CWE: CWE-200, CWE-612
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-2xmj-8wmq-7475
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=4.9.14 <4.13.56
- Packagist: `contao/contao` — affected >=4.9.14 <4.13.56
- Packagist: `contao/core-bundle` — affected >=5.0.0-RC1 <5.3.38
- Packagist: `contao/core-bundle` — affected >=5.4.0-RC1 <5.6.1
- Packagist: `contao/contao` — affected >=5.0.0-RC1 <5.3.38
- Packagist: `contao/contao` — affected >=5.4.0-RC1 <5.6.1

## Details
### Impact

Protected content elements that are rendered as fragments are indexed and become publicly available in the front end search.

### Patches

Update to Contao 4.13.56, 5.3.38 or 5.6.1.

### Workarounds

Disable the front end search.

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-2xmj-8wmq-7475
- https://nvd.nist.gov/vuln/detail/CVE-2025-57756
- https://github.com/contao/contao/commit/a03976c459b6f3985a28f6488b82a76ffb6c0514
- https://contao.org/en/security-advisories/information-disclosure-in-the-front-end-search-index
- https://github.com/contao/contao
