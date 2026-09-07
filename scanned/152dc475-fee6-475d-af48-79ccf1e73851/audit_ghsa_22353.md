# [M] Symfony DoS

## Summary
Severity: Medium
Advisory: GHSA-r2rq-3h56-fqm4
CVE: CVE-2018-11386
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r2rq-3h56-fqm4
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/symfony` — affected >=3.3.0 <3.3.17
- Packagist: `symfony/symfony` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.0.11
- Packagist: `symfony/http-foundation` — affected >=2.7.0 <2.7.48
- Packagist: `symfony/http-foundation` — affected >=2.8.0 <2.8.41
- Packagist: `symfony/http-foundation` — affected >=3.3.0 <3.3.17
- Packagist: `symfony/http-foundation` — affected >=3.4.0 <3.4.11
- Packagist: `symfony/http-foundation` — affected >=4.0.0 <4.0.11

## Details
An issue was discovered in the HttpFoundation component in Symfony 2.7.x before 2.7.48, 2.8.x before 2.8.41, 3.3.x before 3.3.17, 3.4.x before 3.4.11, and 4.0.x before 4.0.11. The PDOSessionHandler class allows storing sessions on a PDO connection. Under some configurations and with a well-crafted payload, it was possible to do a denial of service on a Symfony application without too much resources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-11386
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2018-11386.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2018-11386.yaml
- https://github.com/symfony/symfony
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G4XNBMFW33H47O5TZGA7JYCVLDBCXAJV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UBQK7JDXIELADIPGZIOUCZKMAJM5LSBW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WU5N2TZFNGXDGMXMPP7LZCWTFLENF6WH
- https://symfony.com/blog/cve-2018-11386-denial-of-service-when-using-pdosessionhandler
- https://symfony.com/cve-2018-11386
- https://www.debian.org/security/2018/dsa-4262
