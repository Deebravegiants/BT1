# [H] CSRF token missing in Symfony

## Summary
Severity: High
Advisory: GHSA-vvmr-8829-6whx
CVE: CVE-2022-23601
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-vvmr-8829-6whx
Type: github-advisory

## Affected
- Packagist: `symfony/framework-bundle` — affected >=5.3.14 <5.3.15
- Packagist: `symfony/framework-bundle` — affected >=5.4.3 <5.4.4
- Packagist: `symfony/framework-bundle` — affected >=6.0.3 <6.0.4

## Details
Description
-----------

The Symfony form component provides a CSRF protection mechanism by using a random token injected in the form and using the session to store and control the token submitted by the user.
When using the FrameworkBundle, this protection can be enabled or disabled with the configuration. If the configuration is not specified, by default, the mechanism is enabled as long as the session is enabled.

In a recent change in the way the configuration is loaded, the default behavior has been dropped and, as a result, the CSRF protection is not enabled in form when not explicitly enabled, which makes the application sensible to CSRF attacks.

Resolution
----------

Symfony restored the default configuration to enable the CSRF protection by default.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/f0ffb775febdf07e57117aabadac96fa37857f50) for branch 5.3.

Credits
-------

We would like to thank Catalin Dan and David Lochner for reporting the issue and Jérémy Derussé for fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-vvmr-8829-6whx
- https://nvd.nist.gov/vuln/detail/CVE-2022-23601
- https://github.com/symfony/symfony/commit/f0ffb775febdf07e57117aabadac96fa37857f50
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/framework-bundle/CVE-2022-23601.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2022-23601.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2022-23601
