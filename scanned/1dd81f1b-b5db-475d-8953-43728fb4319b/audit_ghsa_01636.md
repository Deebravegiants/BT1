# [H] Deserialization of untrusted data in Symfony

## Summary
Severity: High
Advisory: GHSA-w2fr-65vp-mxw3
CVE: CVE-2019-10912
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2020-02-12
Source: https://github.com/advisories/GHSA-w2fr-65vp-mxw3
Type: github-advisory

## Affected
- Packagist: `symfony/cache` — affected >=3.1.0 <3.4.26
- Packagist: `symfony/cache` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/cache` — affected >=4.2.0 <4.2.7
- Packagist: `symfony/phpunit-bridge` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/phpunit-bridge` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/phpunit-bridge` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/phpunit-bridge` — affected >=4.2.0 <4.2.7
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/symfony` — affected >=4.2.0 <4.2.7
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.8
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.8

## Details
In Symfony before 2.8.50, 3.x before 3.4.26, 4.x before 4.1.12, and 4.2.x before 4.2.7, it is possible to cache objects that may contain bad user input. On serialization or unserialization, this could result in the deletion of files that the current user has access to. This is related to symfony/cache and symfony/phpunit-bridge.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10912
- https://github.com/symfony/symfony/commit/4fb975281634b8d49ebf013af9e502e67c28816b
- https://www.debian.org/security/2019/dsa-4441
- https://typo3.org/security/advisory/typo3-core-sa-2019-016
- https://symfony.com/cve-2019-10912
- https://symfony.com/blog/cve-2019-10912-prevent-destructors-with-side-effects-from-being-unserialized
- https://seclists.org/bugtraq/2019/May/21
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZLOZX5BZMQKWG7PJRQL6MB5CAMKBQAWD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RTJGZJLPG5FHKFH7KNAKNTWOGBB6LXAL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MDSM576XIOVXVCMHNJHLBBZBTOD62LDA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LFARAUAWZE4UDSKVDWRD35D75HI5UGSD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BHHIG4GMSGEIDT3RITSW7GJ5NT6IBHXU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BAC2TQVEEH5FDJSSWPM2BCRIPTCOEMMO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6QEAOZXVNDA63537A2OIH4QE77EKZR5O
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/42UEKSLKJB72P24JBWVN6AADHLMYSUQD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZLOZX5BZMQKWG7PJRQL6MB5CAMKBQAWD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RTJGZJLPG5FHKFH7KNAKNTWOGBB6LXAL
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MDSM576XIOVXVCMHNJHLBBZBTOD62LDA
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LFARAUAWZE4UDSKVDWRD35D75HI5UGSD
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BHHIG4GMSGEIDT3RITSW7GJ5NT6IBHXU
