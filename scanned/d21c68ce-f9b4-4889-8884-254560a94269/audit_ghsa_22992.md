# [H] Magento Filter extension bypass via crafted store configuration keys

## Summary
Severity: High
Advisory: GHSA-f8h9-7rpq-7qcc
CVE: CVE-2019-7912
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f8h9-7rpq-7qcc
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.1 <2.1.18
- Packagist: `magento/community-edition` — affected >=2.2 <2.2.9
- Packagist: `magento/community-edition` — affected >=2.3 <2.3.2

## Details
A file upload filter bypass exists in Magento 2.1 prior to 2.1.18, Magento 2.2 prior to 2.2.9, Magento 2.3 prior to 2.3.2. This can be exploited by an authenticated user with admin privileges to edit configuration keys to remove file extension filters, potentially resulting in the malicious upload and execution of malicious files on the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7912
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2019-7912.yaml
- https://github.com/magento/magento2
- https://web.archive.org/web/20201220124205/https://magento.com/security/patches/magento-2.3.2-2.2.9-and-2.1.18-security-update-33
