# [M] Clickstorm SEO Allows Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-vmgw-24w6-9v82
CVE: CVE-2025-30081
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L/E:F/RL:O/RC:C (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-vmgw-24w6-9v82
Type: github-advisory

## Affected
- Packagist: `clickstorm/cs-seo` — affected >=9.0.0 <9.2.0
- Packagist: `clickstorm/cs-seo` — affected >=8.0.0 <8.3.0
- Packagist: `clickstorm/cs-seo` — affected >=7.0.0 <7.4.0
- Packagist: `clickstorm/cs-seo` — affected >=6.0.0 <6.7.0

## Details
A cross-site scripting (XSS) vulnerability has been discovered in the Clickstorm SEO extension. This vulnerabily is exploitable by a logged in backend user utilizing the TYPO3 backend user interface. This user can create output in the HTML context by exploiting improperly encoded user input. Updates 6.7.0, 7.4.0, 8.3.0 and 9.2.0 are available for download.

## References
- https://github.com/clickstorm/cs_seo/commit/46e15a22d52da227b110bf6e95c2bcbb2fe4f55f
- https://github.com/FriendsOfPHP/security-advisories/blob/master/clickstorm/cs-seo/CVE-2025-30081.yaml
- https://github.com/clickstorm/cs_seo
- https://typo3.org/security/advisory/typo3-ext-sa-2025-003
