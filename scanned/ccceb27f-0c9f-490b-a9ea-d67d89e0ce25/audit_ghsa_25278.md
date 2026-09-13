# [H] SimpleSAMLphp Signature validation bypass

## Summary
Severity: High
Advisory: GHSA-j4qf-3w33-8cgc
CVE: CVE-2017-18122
CWE: CWE-347
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j4qf-3w33-8cgc
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <1.14.17

## Details
A signature-validation bypass issue was discovered in SimpleSAMLphp through 1.14.16. A SimpleSAMLphp Service Provider using SAML 1.1 will regard as valid any unsigned SAML response containing more than one signed assertion, provided that the signature of at least one of the assertions is valid. Attributes contained in all the assertions received will be merged and the entityID of the first assertion received will be used, allowing an attacker to impersonate any user of any IdP given an assertion signed by the targeted IdP.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18122
- https://github.com/simplesamlphp/simplesamlphp/commit/e2d53086abbb253efb24ddcb49b116246eb0b6ca
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-18122.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://lists.debian.org/debian-lts-announce/2018/02/msg00008.html
- https://simplesamlphp.org/security/201710-01
- https://www.debian.org/security/2018/dsa-4127
