# [C] SimpleSAMLphp Session fixation issue and authentication bypass in the authcrypt module

## Summary
Severity: Critical
Advisory: GHSA-j96g-47x2-46hv
CVE: CVE-2017-12868
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-j96g-47x2-46hv
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=1.14.12 <1.14.14

## Details
The secureCompare method in lib/SimpleSAML/Utils/Crypto.php in SimpleSAMLphp 1.14.13 and earlier, when used with PHP before 5.6, allows attackers to conduct session fixation attacks or possibly bypass authentication by leveraging missing character conversions before an XOR operation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12868
- https://github.com/simplesamlphp/simplesamlphp/commit/4bc629658e7b7d17c9ac3fe0da7dc5df71f1b85e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-12868.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://lists.debian.org/debian-lts-announce/2017/12/msg00007.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00017.html
- https://simplesamlphp.org/security/201705-01
