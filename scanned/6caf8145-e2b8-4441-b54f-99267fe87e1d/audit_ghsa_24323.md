# [M] SimpleSAMLphp Invalid token creation and validation

## Summary
Severity: Medium
Advisory: GHSA-597c-mh7m-48v7
CVE: CVE-2017-12867
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-597c-mh7m-48v7
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=1.14.0 <1.14.15

## Details
The SimpleSAML_Auth_TimeLimitedToken class in SimpleSAMLphp 1.14.14 and earlier allows attackers with access to a secret token to extend its validity period by manipulating the prepended time offset.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12867
- https://github.com/simplesamlphp/simplesamlphp/commit/608f24c2d5afd70c2af050785d2b12f878b33c68
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-12867.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://lists.debian.org/debian-lts-announce/2017/12/msg00007.html
- https://simplesamlphp.org/security/201708-01
- https://www.debian.org/security/2018/dsa-4127
