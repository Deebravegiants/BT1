# [M] [clickstorm] SEO (cs_seo) TYPO3 extension Cross-site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6p8w-pc35-mqv8
CVE: CVE-2025-48203
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L/E:F/RL:O/RC:C (CVSS_V3)
Published: 2025-05-21
Source: https://github.com/advisories/GHSA-6p8w-pc35-mqv8
Type: github-advisory

## Affected
- Packagist: `clickstorm/cs-seo` — affected >=9.0.0 <9.3.0
- Packagist: `clickstorm/cs-seo` — affected >=8.0.0 <8.4.0
- Packagist: `clickstorm/cs-seo` — affected >=7.0.0 <7.5.0
- Packagist: `clickstorm/cs-seo` — affected >=6.3.0 <6.8.0

## Details
Cross-site scripting (XSS) vulnerability in the [clickstorm] SEO (cs_seo) TYPO3 extension allows backend users to execute arbitrary script via the JSON-LD output.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-48203
- https://github.com/clickstorm/cs_seo/commit/1cf6c40821102b1f1508fe4e76825569340c8f90
- https://github.com/FriendsOfPHP/security-advisories/blob/master/clickstorm/cs-seo/CVE-2025-48203.yaml
- https://github.com/clickstorm/cs_seo
- https://typo3.org/security/advisory/typo3-ext-sa-2025-005
