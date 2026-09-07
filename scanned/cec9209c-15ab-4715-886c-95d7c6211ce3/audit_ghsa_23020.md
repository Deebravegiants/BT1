# [M] Magento Unauthorized access to restricted resources

## Summary
Severity: Medium
Advisory: GHSA-q9xx-4689-gvv5
CVE: CVE-2021-28563
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q9xx-4689-gvv5
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.4.0 <2.4.2-p1
- Packagist: `magento/community-edition` — affected >=0 <2.3.7

## Details
Magento versions 2.4.2 (and earlier), 2.4.1-p1 (and earlier) and 2.3.6-p1 (and earlier) are affected by an Improper Authorization vulnerability via the 'Create Customer' endpoint. Successful exploitation could lead to unauthorized modification of customer data by an unauthenticated attacker. Access to the admin console is required for successful exploitation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28563
- https://github.com/magento/magento2/commit/1bd5cb8c065e44779526c0b044ce19b884707695
- https://github.com/magento/magento2/commit/ed952726c94e401e922e88490e41a536f2d850e7
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb21-30.html
