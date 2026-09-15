# [H] SimpleSAMLphp SAML2 library Regular Expression Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-hhm8-2j4g-mpgg
CVE: CVE-2018-6519
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-hhm8-2j4g-mpgg
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/saml2` — affected >=0 <1.10.4
- Packagist: `simplesamlphp/saml2` — affected >=2.0 <2.3.5
- Packagist: `simplesamlphp/saml2` — affected >=3.0 <3.1.1

## Details
The SAML2 library before 1.10.4, 2.x before 2.3.5, and 3.x before 3.1.1 in SimpleSAMLphp has a Regular Expression Denial of Service vulnerability for fraction-of-seconds data in a timestamp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6519
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/saml2/CVE-2018-6519.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://simplesamlphp.org/security/201801-01
- https://www.debian.org/security/2018/dsa-4127
