# [M] Magento Open Source Information Exposure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4f89-5cwm-rm5g
CVE: CVE-2024-45134
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-10
Source: https://github.com/advisories/GHSA-4f89-5cwm-rm5g
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.7-beta1 <2.4.7-p3
- Packagist: `magento/community-edition` — affected >=2.4.6-p1 <2.4.6-p8
- Packagist: `magento/community-edition` — affected >=2.4.5-p1 <2.4.5-p10
- Packagist: `magento/community-edition` — affected >=0 <2.4.4-p11
- Packagist: `magento/community-edition` — affected 2.4.7
- Packagist: `magento/community-edition` — affected 2.4.6
- Packagist: `magento/community-edition` — affected 2.4.5
- Packagist: `magento/community-edition` — affected 2.4.4

## Details
Magento Open Source versions 2.4.7-p2, 2.4.6-p7, 2.4.5-p9, 2.4.4-p10 and earlier are affected by an Information Exposure vulnerability that could result in a security feature bypass. An admin attacker could leverage this vulnerability to have a low impact on confidentiality which may aid in further attacks. Exploitation of this issue does not require user interaction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45134
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb24-73.html
