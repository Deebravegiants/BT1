# [M] Insecure Direct Object Reference in extension "Content Consent" (content_consent)

## Summary
Severity: Medium
Advisory: GHSA-j8cw-ppmv-wj85
CVE: CVE-2023-50462
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-j8cw-ppmv-wj85
Type: github-advisory

## Affected
- Packagist: `t3s/content-consent` — affected >=2.0.0 <2.0.2
- Packagist: `t3s/content-consent` — affected >=0 <1.0.3

## Details
The extension fails to verify whether a specified content element identifier is permitted by the plugin. This enables an unauthenticated user to display various content elements, leading to an insecure direct object reference (IDOR) vulnerability with the potential to expose internal content elements.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/t3s/content-consent/CVE-2023-50462.yaml
- https://typo3.org/security/advisory/typo3-ext-sa-2023-009
