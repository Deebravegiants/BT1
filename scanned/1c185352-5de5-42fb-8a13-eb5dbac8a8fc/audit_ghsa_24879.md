# [C] Magento deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9wc9-498w-h8xv
CVE: CVE-2020-3716
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9wc9-498w-h8xv
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.2.0 <2.2.11
- Packagist: `magento/community-edition` — affected >=2.3.0 <2.3.4

## Details
Magento versions 2.3.3 and earlier, 2.2.10 and earlier, 1.14.4.3 and earlier, and 1.9.4.3 and earlier have a deserialization of untrusted data vulnerability. Successful exploitation could lead to arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-3716
- https://github.com/magento/magento2
- https://helpx.adobe.com/security/products/magento/apsb20-02.html
