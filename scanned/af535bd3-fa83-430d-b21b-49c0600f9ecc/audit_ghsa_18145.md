# [C] Magento Community Edition Improper Input Validation vulnerability

## Summary
Severity: Critical
Advisory: GHSA-wh92-6q6g-px7j
CVE: CVE-2025-54236
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-wh92-6q6g-px7j
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected >=2.4.6-p1
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected >=2.4.9-alpha1
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.8
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1
- Packagist: `magento/community-edition` — affected >=2.4.8-beta1
- Packagist: `magento/community-edition` — affected 2.4.9
- Packagist: `magento/project-community-edition` — affected >=0

## Details
Adobe Commerce versions 2.4.9-alpha2, 2.4.8-p2, 2.4.7-p7, 2.4.6-p12, 2.4.5-p14, 2.4.4-p15 and earlier are affected by an Improper Input Validation vulnerability that could result in a Security feature bypass. A successful attacker can abuse this to achieve session takeover, increasing the confidentiality and integrity impact to high. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54236
- https://experienceleague.adobe.com/en/docs/experience-cloud-kcs/kbarticles/ka-27397
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb25-88.html
- https://nullsecurityx.codes/cve-2025-54236-sessionreaper-unauthenticated-rce-in-magento
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-54236
