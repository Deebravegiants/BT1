# [M] Authentication granted to all firewalls instead of just one

## Summary
Severity: Medium
Advisory: GHSA-rfcf-m67m-jcrq
CVE: CVE-2021-32693
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-rfcf-m67m-jcrq
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=5.3.0 <5.3.2
- Packagist: `symfony/symfony` — affected >=5.3.0 <5.3.2

## Details
Description
-----------

When an application defines multiple firewalls, the authenticated token delivered by one of the firewalls is available to all other firewalls. This can be abused when the application defines different providers for different parts of an application. In such a situation, a user authenticated on one part of the application is considered authenticated on the whole application.

Resolution
----------

We now ensure that the authenticated token is only available for the firewall that generates it.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/3084764ad82f29dbb025df19978b9cbc3ab34728) for branch 5.3.

Credits
-------

I would like to thank Bogdan, gndk, Paweł Warchoł, Warxcell, and Adrien Lamotte for reporting the issue and Wouter J for fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-rfcf-m67m-jcrq
- https://nvd.nist.gov/vuln/detail/CVE-2021-32693
- https://github.com/symfony/security-http/commit/6bf4c31219773a558b019ee12e54572174ff8129
- https://github.com/symfony/symfony/commit/3084764ad82f29dbb025df19978b9cbc3ab34728
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2021-32693.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2021-32693.yaml
- https://github.com/symfony/security-http
- https://symfony.com/blog/cve-2021-32693-authentication-granted-to-all-firewalls-instead-of-just-one
- https://symfony.com/cve-2021-32693
