# [C] SimpleSAMLphp Use of insecure connection charset (sqlauth module)

## Summary
Severity: Critical
Advisory: GHSA-qv5p-6wrc-79wg
CVE: CVE-2018-6521
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qv5p-6wrc-79wg
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=0 <1.15.2

## Details
The sqlauth module in SimpleSAMLphp before 1.15.2 relies on the MySQL utf8 charset, which truncates queries upon encountering four-byte characters. There might be a scenario in which this allows remote attackers to bypass intended access restrictions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-6521
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/CVE-2018-6521.yaml
- https://github.com/simplesamlphp/simplesamlphp
- https://lists.debian.org/debian-lts-announce/2018/02/msg00008.html
- https://simplesamlphp.org/security/201801-03
- https://www.debian.org/security/2018/dsa-4127
