# [H] SimpleSAMLphp Authentication context bypass in the multiauth module

## Summary
Severity: High
Advisory: GHSA-qc43-78vj-vg7p
CVE: CVE-2017-12869
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qc43-78vj-vg7p
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <1.14.14

## Details
The multiauth module in SimpleSAMLphp 1.14.13 and earlier allows remote attackers to bypass authentication context restrictions and use an authentication source defined in config/authsources.php via vectors related to improper validation of user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12869
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2017-12869.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://github.com/simplesamlphp/simplesamlphp/blob/de98fc5bb663feea16686ae77958f759b4a7638d/docs/simplesamlphp-changelog-1.x.md?plain=1#L902C64-L902C79
- https://lists.debian.org/debian-lts-announce/2017/12/msg00007.html
- https://simplesamlphp.org/security/201704-02
- https://www.debian.org/security/2018/dsa-4127
