# [H] Symfony Vulnerable to Timing Attack

## Summary
Severity: High
Advisory: GHSA-g97c-jfx6-xvxh
CVE: CVE-2015-8125
CWE: CWE-208
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g97c-jfx6-xvxh
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.3.0 <2.3.35
- Packagist: `symfony/symfony` — affected >=2.7.0 <2.7.7
- Packagist: `symfony/form` — affected >=2.3.0 <2.3.35
- Packagist: `symfony/form` — affected >=2.4.0 <2.6.12
- Packagist: `symfony/form` — affected >=2.7.0 <2.7.7
- Packagist: `symfony/security-http` — affected >=2.4.0 <2.6.12
- Packagist: `symfony/security-http` — affected >=2.7.0 <2.7.7
- Packagist: `symfony/security` — affected >=2.3.0 <2.3.35
- Packagist: `symfony/security` — affected >=2.4.0 <2.6.12
- Packagist: `symfony/security` — affected >=2.7.0 <2.7.7
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.6.12

## Details
Symfony 2.3.x before 2.3.35, 2.6.x before 2.6.12, and 2.7.x before 2.7.7 might allow remote attackers to have unspecified impact via a timing attack involving the (1) `Symfony/Component/Security/Http/RememberMe/PersistentTokenBasedRememberMeServices` or (2) `Symfony/Component/Security/Http/Firewall/DigestAuthenticationListener` class in the Symfony Security Component, or (3) legacy CSRF implementation from the `Symfony/Component/Form/Extension/Csrf/CsrfProvider/DefaultCsrfProvider` class in the Symfony Form component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8125
- https://github.com/symfony/symfony/pull/16630
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/form/CVE-2015-8125.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2015-8125.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2015-8125.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2015-8125.yaml
- https://symfony.com/blog/cve-2015-8125-potential-remote-timing-attack-vulnerability-in-security-remember-me-service
- https://symfony.com/cve-2015-8125
- https://web.archive.org/web/20200228050051/http://www.securityfocus.com/bid/77692
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/173271.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/173300.html
- http://www.debian.org/security/2015/dsa-3402
- http://www.securityfocus.com/bid/77692
