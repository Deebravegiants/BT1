# [C] Symfony Incorrect Access Control

## Summary
Severity: Critical
Advisory: GHSA-q87v-q8fw-gmj5
CVE: CVE-2017-11365
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q87v-q8fw-gmj5
Type: github-advisory

## Affected
- Packagist: `symfony/security-core` — affected >=2.7.30 <2.7.32
- Packagist: `symfony/security-core` — affected >=2.8.23 <2.8.25
- Packagist: `symfony/security-core` — affected >=3.2.10 <3.2.12
- Packagist: `symfony/security-core` — affected >=3.3.3 <3.3.5
- Packagist: `symfony/security` — affected >=2.7.30 <2.7.32
- Packagist: `symfony/security` — affected >=2.8.23 <2.8.25
- Packagist: `symfony/security` — affected >=3.2.10 <3.2.12
- Packagist: `symfony/security` — affected >=3.3.3 <3.3.5
- Packagist: `symfony/symfony` — affected >=2.7.30 <2.7.32
- Packagist: `symfony/symfony` — affected >=2.8.23 <2.8.25
- Packagist: `symfony/symfony` — affected >=3.2.10 <3.2.12
- Packagist: `symfony/symfony` — affected >=3.3.3 <3.3.5

## Details
Certain Symfony products are affected by: Incorrect Access Control. This affects Symfony 2.7.30 and Symfony 2.8.23 and Symfony 3.2.10 and Symfony 3.3.3. The type of exploitation is: remote. The component is: Password validator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11365
- https://github.com/symfony/symfony/pull/23507
- https://github.com/symfony/symfony/commit/878198cefae028386c6dc800ccbf18f2b9cbff3f
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-core/CVE-2017-11365.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2017-11365.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2017-11365.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2017-11365-empty-passwords-validation-issue
- https://symfony.com/cve-2017-11365
