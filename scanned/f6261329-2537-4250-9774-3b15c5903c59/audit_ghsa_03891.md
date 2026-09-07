# [H] Unauthenticated crypto and weak IV in Magento\Framework\Encryption

## Summary
Severity: High
Advisory: GHSA-h7qw-mxrm-c6h2
CVE: CVE-2016-6485
CWE: CWE-327
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-11-20
Source: https://github.com/advisories/GHSA-h7qw-mxrm-c6h2
Type: github-advisory

## Affected
- Packagist: `magento/community-edition` — affected >=2.0 <2.2.6
- Packagist: `magento/project-community-edition` — affected >=2.0

## Details
The __construct function in Framework/Encryption/Crypt.php in Magento 2 uses the PHP rand function to generate a random number for the initialization vector, which makes it easier for remote attackers to defeat cryptographic protection mechanisms by guessing the value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6485
- https://github.com/magento/magento2/pull/15017
- https://github.com/FriendsOfPHP/security-advisories/blob/master/magento/product-community-edition/CVE-2016-6485.yaml
- http://www.openwall.com/lists/oss-security/2016/07/19/3
- http://www.openwall.com/lists/oss-security/2016/07/27/14
