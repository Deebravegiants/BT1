# [H] Improper authentication in Symfony

## Summary
Severity: High
Advisory: GHSA-cchx-mfrc-fwqr
CVE: CVE-2019-10911
CWE: CWE-200, CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-12
Source: https://github.com/advisories/GHSA-cchx-mfrc-fwqr
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/security-http` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/security-http` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/security-http` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/security-http` — affected >=4.2.0 <4.2.7
- Packagist: `symfony/security` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/security` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/security` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/security` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/security` — affected >=4.2.0 <4.2.7
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.51
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.50
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.4.26
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.1.12
- Packagist: `symfony/symfony` — affected >=4.2.0 <4.2.7

## Details
In Symfony before 2.7.51, 2.8.x before 2.8.50, 3.x before 3.4.26, 4.x before 4.1.12, and 4.2.x before 4.2.7, a vulnerability would allow an attacker to authenticate as a privileged user on sites with user registration and remember me login functionality enabled. This is related to symfony/security.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10911
- https://github.com/symfony/symfony/commit/a29ce2817cf43bb1850cf6af114004ac26c7a081
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2019-10911.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2019-10911.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2019-10911.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2019-10911-add-a-separator-in-the-remember-me-cookie-hash
- https://symfony.com/cve-2019-10911
- https://www.synology.com/security/advisory/Synology_SA_19_19
