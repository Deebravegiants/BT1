# [H] Symfony Directory Traversal

## Summary
Severity: High
Advisory: GHSA-c49r-8gj6-768r
CVE: CVE-2017-16654
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c49r-8gj6-768r
Type: github-advisory

## Affected
- Packagist: `symfony/intl` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/intl` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/intl` — affected >=3.0.0 <3.2.14
- Packagist: `symfony/intl` — affected >=3.3.0 <3.3.13
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.38
- Packagist: `symfony/symfony` — affected >=2.8.0 <2.8.31
- Packagist: `symfony/symfony` — affected >=3.0.0 <3.2.14
- Packagist: `symfony/symfony` — affected >=3.3.0 <3.3.13

## Details
An issue was discovered in Symfony before 2.7.38, 2.8.31, 3.2.14, 3.3.13, 3.4-BETA5, and 4.0-BETA5. The Intl component includes various bundle readers that are used to read resource bundles from the local filesystem. The read() methods of these classes use a path and a locale to determine the language bundle to retrieve. The locale argument value is commonly retrieved from untrusted user input (like a URL parameter). An attacker can use this argument to navigate to arbitrary directories via the dot-dot-slash attack, aka Directory Traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16654
- https://github.com/symfony/symfony/pull/24994
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/intl/CVE-2017-16654.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2017-16654.yaml
- https://github.com/symfony/symfony
- https://lists.debian.org/debian-lts-announce/2019/03/msg00009.html
- https://symfony.com/blog/cve-2017-16654-intl-bundle-readers-breaking-out-of-paths
- https://symfony.com/cve-2017-16654
- https://www.debian.org/security/2018/dsa-4262
