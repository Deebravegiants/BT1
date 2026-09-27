# [M] Ez Platform Object Injection in legacy shop module

## Summary
Severity: Medium
Advisory: GHSA-39j2-4p9j-5w4j
CWE: CWE-94
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-39j2-4p9j-5w4j
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2019.3.0 <2019.3.5.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2017.12.0 <2017.12.7.3
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.4.0 <5.4.14.2

## Details
This Security Advisory is about a vulnerability in the Legacy shop module. A backend editor could perform object injection in discount rules. This would require backend access and permission to edit discount rules. While object injection in itself is a serious vulnerability, the permission requirement means that normally only administrators would be able to exploit it, that's why it was classified as Medium severity.

## References
- https://ezplatform.com/security-advisories/ibexa-sa-2020-006-object-injection-in-legacy-shop-module
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezpublish-legacy/2020-10-05-1.yaml
- https://github.com/ezsystems/ezpublish-legacy
