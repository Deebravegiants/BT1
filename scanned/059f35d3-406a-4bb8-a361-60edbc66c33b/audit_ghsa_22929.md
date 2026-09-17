# [H] Symfony collectionCascaded and collectionCascadedDeeply fields security bypass

## Summary
Severity: High
Advisory: GHSA-q8j7-fjh7-25v5
CVE: CVE-2013-4751
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-q8j7-fjh7-25v5
Type: github-advisory

## Affected
- Packagist: `symfony/validator` — affected >=2.0.0 <2.0.24
- Packagist: `symfony/validator` — affected >=2.1.0 <2.1.12
- Packagist: `symfony/validator` — affected >=2.2.0 <2.2.5
- Packagist: `symfony/validator` — affected >=2.3.0 <2.3.3
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.24
- Packagist: `symfony/symfony` — affected >=2.1.0 <2.1.12
- Packagist: `symfony/symfony` — affected >=2.2.0 <2.2.5
- Packagist: `symfony/symfony` — affected >=2.3.0 <2.3.3

## Details
When using the Validator component, if `Symfony\\Component\\Validator\\Mapping\\Cache\\ApcCache` is enabled (or any other cache implementing `Symfony\\Component\\Validator\\Mapping\\Cache\\CacheInterface`), some information is lost during serialization (the `collectionCascaded` and the `collectionCascadedDeeply` fields).

As a consequence, arrays or traversable objects stored in fields using the `@Valid` constraint are not traversed by the validator as soon as the validator configuration is loaded from the cache.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4751
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-4751
- https://exchange.xforce.ibmcloud.com/vulnerabilities/86364
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2013-4751.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/validator/CVE-2013-4751.yaml
- https://github.com/symfony/validator
- https://symfony.com/blog/security-releases-symfony-2-0-24-2-1-12-2-2-5-and-2-3-3-released
- https://web.archive.org/web/20200228181137/http://www.securityfocus.com/bid/61709
- http://lists.fedoraproject.org/pipermail/package-announce/2013-August/114380.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-August/114436.html
- http://symfony.com/blog/security-releases-symfony-2-0-24-2-1-12-2-2-5-and-2-3-3-released
