# [M] Contao can disclose sensitive information in the news module

## Summary
Severity: Medium
Advisory: GHSA-w53m-gxvg-vx7p
CVE: CVE-2025-57757
CWE: CWE-200, CWE-212
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-w53m-gxvg-vx7p
Type: github-advisory

## Affected
- Packagist: `contao/core-bundle` — affected >=5.0.0-RC1 <5.3.38
- Packagist: `contao/core-bundle` — affected >=5.4.0-RC1 <5.6.1
- Packagist: `contao/contao` — affected >=5.0.0-RC1 <5.3.38
- Packagist: `contao/contao` — affected >=5.4.0-RC1 <5.6.1

## Details
### Impact

If a news feed contains protected news archives, their news items are not filtered and become publicly available in the RSS feed.

### Patches

Update to Contao 5.3.38 or 5.6.1.

### Workarounds

Do not add protected news archives to the news feed page.

### For more information

If you have any questions or comments about this advisory, open an issue in [contao/contao](https://github.com/contao/contao/issues/new/choose).

## References
- https://github.com/contao/contao/security/advisories/GHSA-w53m-gxvg-vx7p
- https://nvd.nist.gov/vuln/detail/CVE-2025-57757
- https://github.com/contao/contao/commit/e75f46b11974fbf7a4652e65c19ad6ca84c59271
- https://contao.org/en/security-advisories/information-disclosure-in-the-news-module
- https://github.com/contao/contao
