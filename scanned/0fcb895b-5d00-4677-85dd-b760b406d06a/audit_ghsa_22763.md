# [H] Magento is affected by an improper input validation vulnerability

## Summary
Severity: High
Advisory: GHSA-5vw8-r55w-f4q4
CVE: CVE-2021-36032
CWE: CWE-20, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5vw8-r55w-f4q4
Type: github-advisory

## Affected
- Packagist: `magento/project-community-edition` — affected >=0
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p1
- Packagist: `magento/community-edition` — affected 2.3.7
- Packagist: `magento/community-edition` — affected >=2.4.2-p1 <2.4.2-p2
- Packagist: `magento/community-edition` — affected 2.4.2

## Details
Magento Commerce versions 2.4.2 (and earlier), 2.4.2-p1 (and earlier) and 2.3.7 (and earlier) are affected by an improper input validation vulnerability. An authenticated attacker can trigger an insecure direct object reference in the `V1/customers/me` endpoint to achieve information exposure and privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36032
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-64.html
