# [M] onelogin/php-saml signature wrapping attacks

## Summary
Severity: Medium
Advisory: GHSA-g48f-pgwh-wwxx
CVE: CVE-2016-1000253
Ecosystem: Packagist
Published: 2024-05-17
Source: https://github.com/advisories/GHSA-g48f-pgwh-wwxx
Type: github-advisory

## Affected
- Packagist: `onelogin/php-saml` — affected >=0 <2.10.0

## Details
Vulnerability in onelogin/php-saml versions prior to 2.10.0 allows signature Wrapping attacks which may result in a malicious user gaining unauthorized access to a system.

## References
- https://github.com/onelogin/php-saml/commit/9d31baa97a57b0989020f62d24307c29e325dac3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/onelogin/php-saml/CVE-2016-1000253.yaml
- https://github.com/SAML-Toolkits/php-saml
