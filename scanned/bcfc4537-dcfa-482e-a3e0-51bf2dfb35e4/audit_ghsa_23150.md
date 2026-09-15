# [M] FriendsOfSymfony FOSUserBundle denial of service via login form

## Summary
Severity: Medium
Advisory: GHSA-9mpf-g3fc-9rgv
CVE: CVE-2013-5750
CWE: CWE-400
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9mpf-g3fc-9rgv
Type: github-advisory

## Affected
- Packagist: `friendsofsymfony/user-bundle` — affected >=1.2.0 <1.2.5
- Packagist: `friendsofsymfony/user-bundle` — affected >=1.3.0 <1.3.3

## Details
The login form in the FriendsOfSymfony FOSUserBundle bundle before 1.3.3 for Symfony allows remote attackers to cause a denial of service (CPU consumption) via a long password that triggers an expensive hash computation, as demonstrated by a PBKDF2 computation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5750
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsofsymfony/user-bundle/CVE-2013-5750.yaml
- https://symfony.com/cve-2013-5750
- http://symfony.com/blog/cve-2013-5750-security-issue-in-fosuserbundle-login-form
