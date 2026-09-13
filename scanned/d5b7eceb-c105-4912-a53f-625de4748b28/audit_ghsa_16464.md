# [H] Code injection in the way Symfony implements translation caching in FrameworkBundle

## Summary
Severity: High
Advisory: GHSA-wfv7-5x33-v22h
CVE: CVE-2014-4931
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-wfv7-5x33-v22h
Type: github-advisory

## Affected
- Packagist: `symfony/framework-bundle` — affected >=2.0.0 <2.3.18
- Packagist: `symfony/framework-bundle` — affected >=2.4.0 <2.4.8
- Packagist: `symfony/framework-bundle` — affected >=2.5.0 <2.5.2
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.3.19
- Packagist: `symfony/symfony` — affected >=2.4.0 <2.4.9
- Packagist: `symfony/symfony` — affected >=2.5.0 <2.5.4

## Details
When investigating issue [#11093](https://github.com/symfony/symfony/issues/11093), [Jeremy Derussé](https://connect.sensiolabs.com/profile/jderusse) found a serious code injection issue in the way Symfony implements translation caching in FrameworkBundle.

- Your Symfony application is vulnerable if you meet the following conditions:

- You are using the Symfony translation system from FrameworkBundle (so basically if you are using Symfony full-stack -- you are not affected if you are using the Translation component with Silex for instance);
You don't sanitize locales coming from a URL (any route with a _locale argument for instance):

When vulnerable, an attacker can submit a non-valid locale value that can contain some PHP code that will be executed by Symfony. That's because the locale value is dumped into a PHP file generated in the cache without being sanitized first.

## References
- https://github.com/symfony/symfony/commit/06a80fbdbe744ad6f3010479ba64ef5cf35dd9af.patch
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/framework-bundle/CVE-2014-4931.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2014-4931.yaml
- https://symfony.com/blog/security-releases-cve-2014-4931-symfony-2-3-18-2-4-8-and-2-5-2-released
