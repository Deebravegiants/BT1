# [H] Magento Improper input validation vulnerability

## Summary
Severity: High
Advisory: GHSA-297f-r9w7-w492
CVE: CVE-2022-42344
CWE: CWE-20, CWE-639, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-20
Source: https://github.com/advisories/GHSA-297f-r9w7-w492
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=0 <2.3.7-p4
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.3-p3
- Packagist: `magento/community-edition` — affected >=2.4.4 <2.4.5

## Details
Adobe Commerce versions 2.4.3-p2 (and earlier), 2.3.7-p3 (and earlier) and 2.4.4 (and earlier) are affected by an improper input validation vulnerability. An authenticated attacker can trigger an insecure direct object reference in the `V1/customers/me` endpoint to achieve information exposure and privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42344
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb22-38.html
