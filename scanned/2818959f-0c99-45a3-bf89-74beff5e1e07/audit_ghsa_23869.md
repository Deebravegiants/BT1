# [C] SimpleSAMLphp SAML2 spoof SAML responses

## Summary
Severity: Critical
Advisory: GHSA-r8v4-7vwj-983x
CVE: CVE-2016-9814
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r8v4-7vwj-983x
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/saml2` — affected >=1.10 <1.10.3
- Packagist: `simplesamlphp/saml2` — affected >=0 <1.8.1
- Packagist: `simplesamlphp/saml2` — affected >=1.9.0 <1.9.1
- Packagist: `simplesamlphp/saml2` — affected >=2.0 <2.3.3

## Details
The validateSignature method in the SAML2\Utils class in SimpleSAMLphp before 1.14.10 and simplesamlphp/saml2 library before 1.9.1, 1.10.x before 1.10.3, and 2.x before 2.3.3 allows remote attackers to spoof SAML responses or possibly cause a denial of service (memory consumption) by leveraging improper conversion of return values to boolean.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9814
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/saml2/CVE-2016-9814.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://lists.debian.org/debian-lts-announce/2018/03/msg00001.html
- https://simplesamlphp.org/security/201612-01
- http://www.securityfocus.com/bid/94730
