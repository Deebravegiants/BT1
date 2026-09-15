# [C] Symfony Service IDs Allow Injection

## Summary
Severity: Critical
Advisory: GHSA-pgwj-prpq-jpc2
CVE: CVE-2019-10910
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-18
Source: https://github.com/advisories/GHSA-pgwj-prpq-jpc2
Type: github-advisory

## Affected
- Packagist: `symfony/dependency-injection` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/dependency-injection` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/dependency-injection` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/dependency-injection` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/dependency-injection` — affected >=4.2.0 <4.2.7
- Packagist: `symfony/proxy-manager-bridge` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/proxy-manager-bridge` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/proxy-manager-bridge` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/proxy-manager-bridge` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/proxy-manager-bridge` — affected >=4.2.0 <4.2.7
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/symfony` — affected >=4.2.0 <4.2.7

## Details
In Symfony before 2.7.51, 2.8.x before 2.8.50, 3.x before 3.4.26, 4.x before 4.1.12, and 4.2.x before 4.2.7, when service ids allow user input, this could allow for SQL Injection and remote code execution. This is related to symfony/dependency-injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10910
- https://github.com/symfony/symfony/commit/3876c75f858d5d82e2c309698d21af2f1d721afb
- https://github.com/symfony/symfony/commit/4c80c3444854ef384df94deb4acbcef4b5e5243b
- https://github.com/symfony/symfony/commit/d2fb5893923292a1da7985f0b56960b5bb10737b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/dependency-injection/CVE-2019-10910.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/proxy-manager-bridge/CVE-2019-10910.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-10910.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2019-10910-check-service-ids-are-valid
- https://symfony.com/cve-2019-10910
- https://www.synology.com/security/advisory/Synology_SA_19_19
