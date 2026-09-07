# [M] Symfony2 improper IP based access control

## Summary
Severity: Medium
Advisory: GHSA-hx53-jchx-cr52
CWE: CWE-291
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-hx53-jchx-cr52
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.19
- Packagist: `symfony/symfony` — affected >=2.1.0 <2.1.4

## Details
Damien Tournoud, from the Drupal security team, contacted us two days ago about a security issue in the Request::getClientIp() method when the trust proxy mode is enabled (Request::trustProxyData()).

An application is vulnerable if it uses the client IP address as returned by the Request::getClientIp() method for sensitive decisions like IP based access control.

To fix this security issue, the following changes have been made to all versions of Symfony2:

A new Request::setTrustedProxies() method has been introduced and should be used intead of Request::trustProxyData() to enable the trust proxy mode. It takes an array of trusted proxy IP addresses as its argument:
```
// before (probably in your front controller script)
Request::trustProxyData();
```
```
// after
Request::setTrustedProxies(array('1.1.1.1'));
// 1.1.1.1 being the IP address of a trusted reverse proxy
```
The Request::trustProxyData() method has been deprecated (when used, it automatically trusts the latest proxy in the chain -- which is the current remote address):
```
Request::trustProxyData();
```
```
// is equivalent to
Request::setTrustedProxies(array($request->server->get('REMOTE_ADDR')));
```
We encourage all Symfony2 users to upgrade as soon as possible. It you don't want to upgrade to the latest version yet, you can also apply the following patches:

[Patch](https://github.com/symfony/symfony/compare/fc89d6b...9ce892c.patch) for Symfony 2.0.19
[Patch](https://github.com/symfony/symfony/compare/922c201...e5536f0.patch) for Symfony 2.1.4

## References
- https://github.com/symfony/symfony/commit/922c2015f61a7205180d423dce1f7365cc2d8460
- https://github.com/symfony/symfony/commit/9ce892cf4395e73b136e9b5cd1fae9e91995c93b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/2012-11-29.yaml
- https://github.com/symfony/symfony
- https://symfony.com/blog/security-release-symfony-2-0-19-and-2-1-4
