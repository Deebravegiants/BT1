# [M] PayPal PHP Merchant SDK Cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-p4g7-wjhq-9r2h
CVE: CVE-2017-6099
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p4g7-wjhq-9r2h
Type: github-advisory

## Affected
- Packagist: `paypal/merchant-sdk-php` — affected >=3.0.0 <3.12.0

## Details
Cross-site scripting (XSS) vulnerability in GetAuthDetails.html.php in PayPal PHP Merchant SDK (aka merchant-sdk-php) 3.9.1 allows remote attackers to inject arbitrary web script or HTML via the token parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6099
- https://github.com/paypal/merchant-sdk-php/issues/129
- https://github.com/FriendsOfPHP/security-advisories/blob/master/paypal/merchant-sdk-php/CVE-2017-6099.yaml
- http://www.securityfocus.com/bid/96432
