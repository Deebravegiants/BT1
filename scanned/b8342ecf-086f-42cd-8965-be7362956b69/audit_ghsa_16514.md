# [H] Symfony XML Entity Expansion security vulnerability

## Summary
Severity: High
Advisory: GHSA-q2gc-gg3x-7942
CWE: CWE-776
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-q2gc-gg3x-7942
Type: github-advisory

## Affected
- Packagist: `symfony/symfony` — affected >=2.0.0 <2.0.17

## Details
Symfony 2.0.11 carried a [similar] XXE security fix, however, on review of ZF2 I also noted a vulnerability to XML Entity Expansion (XEE) attacks whereby all extensions making use of libxml2 have no defense against XEE Quadratic Blowup Attacks. The vulnerability is a function of there being no current method of disabling custom entities in PHP (i.e. defined internal to the XML document without using external entities). In a QBA, a long entity can be defined and then referred to multiple times in document elements, creating a memory sink with which Denial Of Service attacks against a host's RAM can be mounted. The use of the LIBXML_NOENT or equivalent option in a dependent extension amplified the impact (it doesn't actually mean "No Entities"). In addition, libxml2's innate defense against the related Exponential or Billion Laugh's XEE attacks is active only so long as the LIBXML_PARSEHUGE is NOT set (it disables libxml2's hardcoded entity recursion limit). No instances of these two options were noted, but it's worth referencing for the future.

Consider this (non-fatal) example:

<?xml version="1.0"?>
<!DOCTYPE data [<!ENTITY a
"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa">]>
<data>&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;</data>
Increase the length of entity, and entity count to a few hundred, and peak memory usage will waste no time spiking the moment the nodeValue for is accessed since the entities will then be expanded by a simple multiplier effect. No external entities required.

...

This can be used in combination with the usual XXE defense of calling libxml_disable_entity_loader(TRUE) and, optionally, the LIBXML_NONET option (should local filesystem access be allowable). The DOCTYPE may be removed instead of rejecting the XML outright but this would likely result in other problems with the unresolved entities.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/2012-08-28.yaml
- https://github.com/symfony/symfony
- https://github.com/symfony/symfony/blob/2.0/CHANGELOG-2.0.md
- https://github.com/symfony/symfony/compare/352e8f583c87c709de197bb16c4053d2e87fd4cd...5bf4f92e86c34690d71e8f94350ec975909a435b.diff
- https://symfony.com/blog/security-release-symfony-2-0-17-released
