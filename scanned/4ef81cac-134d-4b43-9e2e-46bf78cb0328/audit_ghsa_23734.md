# [H] Symphony Denial of Service Via Overlong Usernames

## Summary
Severity: High
Advisory: GHSA-whgv-8cg3-7hcm
CVE: CVE-2016-4423
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-whgv-8cg3-7hcm
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=2.3.0 <2.3.41
- Packagist: `symfony/security-http` — affected >=2.4.0 <2.7.13
- Packagist: `symfony/security-http` — affected >=2.8.0 <2.8.6
- Packagist: `symfony/security-http` — affected >=3.0.0 <3.0.6
- Packagist: `symfony/security` — affected >=2.3.0 <2.3.41
- Packagist: `symfony/security` — affected >=2.4.0 <2.7.13
- Packagist: `symfony/security` — affected >=2.8.0 <2.8.6
- Packagist: `symfony/security` — affected >=3.0.0 <3.0.6
- Packagist: `symfony/symfony` — affected >=2.3.0 <2.3.41
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.7.13
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.6
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.0.6

## Details
The attemptAuthentication function in `Component/Security/Http/Firewall/UsernamePasswordFormAuthenticationListener.php` in Symfony before 2.3.41, 2.7.x before 2.7.13, 2.8.x before 2.8.6, and 3.0.x before 3.0.6 does not limit the length of a username stored in a session, which allows remote attackers to cause a denial of service (session storage consumption) via a series of authentication attempts with long, non-existent usernames.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4423
- https://github.com/symfony/symfony/pull/18733
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2016-4423.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2016-4423.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2016-4423.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/cve-2016-4423-large-username-storage-in-session
- https://symfony.com/cve-2016-4423
- http://www.debian.org/security/2016/dsa-3588
