# [H] Symfony Arbitrary PHP code Execution

## Summary
Severity: High
Advisory: GHSA-7w53-hfpw-rg3g
CVE: CVE-2013-1397
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-7w53-hfpw-rg3g
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.2.0-BETA1 <2.2.0-BETA2
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.22
- Packagist: `symfony/symfony` — affected >=2.1.0 <2.1.7
- Packagist: `symfony/yaml` — affected >=2.0.0 <2.0.22
- Packagist: `symfony/yaml` — affected >=2.1.0 <2.1.7
- Packagist: `symfony/yaml` — affected >=2.2.0-BETA1 <2.2.0-BETA2

## Details
Symfony 2.0.x before 2.0.22, 2.1.x before 2.1.7, and 2.2.x remote attackers to execute arbitrary PHP code via a serialized PHP object to the (1) Yaml::parse or (2) Yaml\Parser::parse function, a different vulnerability than CVE-2013-1348.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1397
- https://github.com/symfony/symfony/commit/ba6e3159c0eeb3b6e21db32fce8fa2535cb3aa77
- https://exchange.xforce.ibmcloud.com/vulnerabilities/81551
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2013-1397.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/yaml/CVE-2013-1397.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/security-release-symfony-2-0-22-and-2-1-7-released
- http://symfony.com/blog/security-release-symfony-2-0-22-and-2-1-7-released
