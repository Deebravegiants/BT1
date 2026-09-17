# [M] Cookie persistence after password changes in symfony/security-bundle

## Summary
Severity: Medium
Advisory: GHSA-qw36-p97w-vcqr
CVE: CVE-2021-41268
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-11-24
Source: https://github.com/advisories/GHSA-qw36-p97w-vcqr
Type: github-advisory

## Affected
- Packagist: `symfony/security-bundle` — affected >=5.3.0 <5.3.12
- Packagist: `symfony/symfony` — affected >=5.3.0 <5.3.12

## Details
Description
-----------

Since the rework of the Remember me cookie in Symfony 5.3, the cookie is not invalidated anymore when the user changes its password. 

Attackers can therefore maintain their access to the account even if the password is changed as long as they have had the chance to login once and get a valid remember me cookie.

Resolution
----------

Symfony now makes the password part of the signature by default. In that way, when the password changes then the cookie is not valid anymore.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/36a808b857cd3240244f4b224452fb1e70dc6dfc) for branch 5.3.

Credits
-------

We would like to thank Thibaut Decherit for reporting the issue and Wouter J for fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-qw36-p97w-vcqr
- https://nvd.nist.gov/vuln/detail/CVE-2021-41268
- https://github.com/symfony/symfony/pull/44243
- https://github.com/symfony/symfony/commit/36a808b857cd3240244f4b224452fb1e70dc6dfc
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-bundle/CVE-2021-41268.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2021-41268.yaml
- https://github.com/symfony/symfony
- https://github.com/symfony/symfony/releases/tag/v5.3.12
- https://symfony.com/cve-2021-41268
