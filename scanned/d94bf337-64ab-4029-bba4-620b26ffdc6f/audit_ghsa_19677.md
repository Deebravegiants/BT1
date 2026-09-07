# [M] Additional TCA Allows Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-rrh3-cgmx-w62f
CVE: CVE-2025-30083
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L/E:F/RL:O/RC:C (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-rrh3-cgmx-w62f
Type: github-advisory

## Affected
- Packagist: `codingms/additional-tca` — affected >=1.16.0 <1.16.9
- Packagist: `codingms/additional-tca` — affected >=1.7.0 <1.15.17

## Details
A cross-site scripting (XSS) vulnerability has been discovered in the Additional TCA extension. This vulnerabily is exploitable by a logged in backend user utilizing the TYPO3 backend user interface. This user can create output in the HTML context by exploiting improperly encoded user input. Updates 1.15.17 and 1.16.9 are available for download.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/codingms/additional-tca/CVE-2025-30083.yaml
- https://gitlab.com/codingms/typo3-public/additional_tca
- https://typo3.org/security/advisory/typo3-ext-sa-2025-002
