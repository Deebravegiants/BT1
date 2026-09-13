# [H] Symphony Vulnerable to PHP Code Injection via YAML Parsing

## Summary
Severity: High
Advisory: GHSA-2r5h-6r7v-5m7c
CVE: CVE-2013-1348
CWE: CWE-94
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-2r5h-6r7v-5m7c
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.22
- Packagist: `symfony/yaml` — affected >=2.0.0 <2.0.22

## Details
The `Yaml::parse` function in Symfony 2.0.x before 2.0.22 remote attackers to execute arbitrary PHP code via a PHP file, a different vulnerability than CVE-2013-1397.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1348
- https://github.com/symfony/symfony/commit/ac756bf39e646b4e130fad058d10a0228dbd9779
- https://exchange.xforce.ibmcloud.com/vulnerabilities/81550
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2013-1348.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/yaml/CVE-2013-1348.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/security-release-symfony-2-0-22-and-2-1-7-released
- https://web.archive.org/web/20150612022223/http://www.securityfocus.com/bid/57574
