# [M] Symfony Allows URI Restrictions Bypass Via Double-Encoded String

## Summary
Severity: Medium
Advisory: GHSA-83c3-qx27-2rwr
CVE: CVE-2012-6431
CWE: CWE-287
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-83c3-qx27-2rwr
Type: github-advisory

## Affected
- Packagist: `symfony/http-foundation` — affected >=2.0.0 <2.0.19
- Packagist: `symfony/routing` — affected >=2.0.0 <2.0.19
- Packagist: `symfony/security` — affected >=2.0.0 <2.0.19
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.19

## Details
On the Symfony 2.0.x version, there's a security issue that allows access to routes protected by a firewall even when the user is not logged in.

Both the Routing component and the Security component uses the path returned by `getPathInfo()` to match a Request. The `getPathInfo()` returns a decoded path, but the Routing component (`Symfony\Component\Routing\Matcher\UrlMatcher`) decodes the path a second time; whereas the Security component, `Symfony\Component\HttpFoundation\RequestMatcher`, does not.

This difference causes Symfony 2.0 to be vulnerable to double encoding attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-6431
- https://github.com/symfony/symfony/commit/55014a6841bec50046e8329a4835c160ac31a496
- https://github.com/symfony/symfony/commit/8b2c17f80377582287a78e0b521497e039dd6b0d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2012-6431.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/routing/CVE-2012-6431.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2012-6431.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2012-6431.yaml
- https://symfony.com/blog/security-release-symfony-2-0-20-and-2-1-5-released
- http://symfony.com/blog/security-release-symfony-2-0-20-and-2-1-5-released
