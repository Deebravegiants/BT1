# [C]  SAML PHP Toolkit Vulnerability on xmlseclibs CVE-2025-66475 

## Summary
Severity: Critical
Advisory: GHSA-5j8p-438x-rgg5
CWE: CWE-1395
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-09
Source: https://github.com/advisories/GHSA-5j8p-438x-rgg5
Type: github-advisory

## Affected
- Packagist: `onelogin/php-saml` — affected >=0 <2.21.1
- Packagist: `onelogin/php-saml` — affected >=3.0.0 <3.8.1
- Packagist: `onelogin/php-saml` — affected >=4.0.0 <4.3.1

## Details
**Summary**

There is a critical vulnerability on xmlseclibs [CVE-2025-66475](https://github.com/robrichards/xmlseclibs/security/advisories/GHSA-c4cc-x928-vjw9), a dependency of php-saml

Update to the following versions of php-saml which forces the use of patched versions of xmlseclibs:
- [2.21.1](https://github.com/SAML-Toolkits/php-saml/releases/tag/2.21.1)
- [3.8.1](https://github.com/SAML-Toolkits/php-saml/releases/tag/3.8.1)
- [4.3.1](https://github.com/SAML-Toolkits/php-saml/releases/tag/4.3.1)


**Impact**

Signature Wrapping Vulnerabilities allows an attacker to impersonate a user.

## References
- https://github.com/SAML-Toolkits/php-saml/security/advisories/GHSA-5j8p-438x-rgg5
- https://github.com/robrichards/xmlseclibs/security/advisories/GHSA-c4cc-x928-vjw9
- https://github.com/SAML-Toolkits/php-saml
- https://github.com/SAML-Toolkits/php-saml/releases/tag/2.21.1
- https://github.com/SAML-Toolkits/php-saml/releases/tag/3.8.1
- https://github.com/SAML-Toolkits/php-saml/releases/tag/4.3.1
