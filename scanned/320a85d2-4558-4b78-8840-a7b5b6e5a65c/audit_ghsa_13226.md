# [H] Composer allows cache poisoning from other projects built on the same host

## Summary
Severity: High
Advisory: GHSA-725m-w832-q973
CVE: CVE-2015-8371
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-21
Source: https://github.com/advisories/GHSA-725m-w832-q973
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=0 <1.0.0

## Details
Composer before 2016-02-10 allows cache poisoning from other projects built on the same host. This results in attacker-controlled code entering a server-side build process. The issue occurs because of the way that dist packages are cached. The cache key is derived from the package name, the dist type, and certain other data from the package repository (which may simply be a commit hash, and thus can be found by an attacker). Versions through 1.0.0-alpha11 are affected, and 1.0.0 is unaffected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8371
- https://flyingmana.de/blog_en/2016/02/14/composer_cache_injection_vulnerability_cve_2015_8371.html
- https://github.com/FriendsOfPHP/security-advisories/blob/e26be423c5bcfdb38478d2f92d1f928c15afb561/composer/composer/CVE-2015-8371.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/composer/composer/CVE-2015-8371.yaml
- https://github.com/composer/composer
- https://gitlab.com/gitlab-org/advisories-community/-/blob/main/packagist/composer/composer/CVE-2015-8371.yml
- http://flyingmana.de/blog_en/2016/02/14/composer_cache_injection_vulnerability_cve_2015_8371.html
