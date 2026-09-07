# [H] Known vulnerable to account takeover via host header injection attack in v1.3.1

## Summary
Severity: High
Advisory: GHSA-p757-4v3p-j74f
CVE: CVE-2022-33011
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-09
Source: https://github.com/advisories/GHSA-p757-4v3p-j74f
Type: github-advisory

## Affected
- Packagist: `idno/known` — affected >=0

## Details
Known v1.3.1 was discovered to allow attackers to perform an account takeover via a host header injection attack.

The researcher report indicates that versions 1.3.1 and prior are vulnerable. Version 1.2.2 is the last version tagged on GitHub and in Packagist, and development related to the 1.3.x branch is currently on the `dev` branch of the idno/known repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33011
- https://blog.jitendrapatro.me/multiple-vulnerabilities-in-idno-known-php-cms-software
- https://github.com/idno/known
- https://github.com/idno/known/blob/dev/composer.json#L4
- https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Account%20Takeover#account-takeover-through-password-reset-poisoning
- https://www.pethuraj.com/blog/how-i-earned-800-for-host-header-injection-vulnerability
