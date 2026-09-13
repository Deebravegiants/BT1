# [M] SimpleSAMLphp allows timing side-channel attacks

## Summary
Severity: Medium
Advisory: GHSA-v882-949x-6v28
CVE: CVE-2017-12872
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-v882-949x-6v28
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <1.15.0-rc1

## Details
The (1) Htpasswd authentication source in the authcrypt module and (2) SimpleSAML_Session class in SimpleSAMLphp 1.14.11 and earlier allow remote attackers to conduct timing side-channel attacks by leveraging use of the standard comparison operator to compare secret material against user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12872
- https://github.com/simplesamlphp/simplesamlphp/commit/b72c79e3070f930d758f5c269333d63ed7509e2e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-12872.yaml
- https://lists.debian.org/debian-lts-announce/2017/12/msg00007.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00017.html
- https://simplesamlphp.org/security/201703-01
