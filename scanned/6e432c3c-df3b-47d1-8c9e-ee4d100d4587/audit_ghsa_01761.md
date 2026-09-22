# [H] Firewall configured with unanimous strategy was not actually unanimous in Symfony

## Summary
Severity: High
Advisory: GHSA-g4m9-5hpf-hx72
CVE: CVE-2020-5275
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2020-03-30
Source: https://github.com/advisories/GHSA-g4m9-5hpf-hx72
Type: github-advisory

## Affected
- Packagist: `symfony/security` — affected >=4.4.0 <4.4.7
- Packagist: `symfony/security` — affected >=5.0.0 <5.0.7
- Packagist: `symfony/security-http` — affected >=4.4.0 <4.4.7
- Packagist: `symfony/security-http` — affected >=5.0.0 <5.0.7
- Packagist: `symfony/symfony` — affected >=4.4.0 <4.4.7
- Packagist: `symfony/symfony` — affected >=5.0.0 <5.0.7

## Details
Description
-----------

On Symfony before 4.4.0, when a `Firewall` checks an access control rule (using the unanimous strategy), it iterates over all rule attributes and grant access only if *all* calls to the `accessDecisionManager` decide to grant access.

As of Symfony 4.4.0, a bug was introduced that prevents the check of attributes as soon as `accessDecisionManager` decide to grant access on one attribute.

Resolution
----------

The `accessDecisionManager` is now called with all attributes at once, allowing the unanimous strategy being applied on each attribute. 

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/c935e4a3fba6cc2ab463a6ca382858068d63cebf) for the 4.4 branch.

Credits
-------

I would like to thank Antonio J. García Lagar for reporting & Robin Chalas for fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-g4m9-5hpf-hx72
- https://nvd.nist.gov/vuln/detail/CVE-2020-5275
- https://github.com/symfony/symfony/commit/c935e4a3fba6cc2ab463a6ca382858068d63cebf
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2020-5275.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2020-5275.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2020-5275.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/C36JLPHUPKDFAX6D5WYFC4ALO2K7RDUQ
- https://symfony.com/cve-2020-5275
