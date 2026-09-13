# [M] eZ Platform REST API returns list of all SiteAccesses

## Summary
Severity: Medium
Advisory: GHSA-9wwx-c723-vm8x
CWE: CWE-200
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-9wwx-c723-vm8x
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-kernel` — affected >=7.3.0 <7.3.2.1
- Packagist: `ezsystems/ezpublish-kernel` — affected >=7.0.0 <7.2.4.1
- Packagist: `ezsystems/ezpublish-kernel` — affected >=6.8.0 <6.13.5.1
- Packagist: `ezsystems/ezpublish-kernel` — affected >=6.0.0 <6.7.9.1
- Packagist: `ezsystems/ezpublish-kernel` — affected >=5.4.0 <5.4.13.1
- Packagist: `ezsystems/ezpublish-kernel` — affected >=5.3.0 <5.3.12.1

## Details
This security advisory fixes a vulnerability in eZ Platform, and we recommend that you install it as soon as possible. The issue is that the REST API may be made to disclose the names of all available site accesses. The severity of this depends on your installation, please consider your response accordingly.

To install, use Composer to update "ezsystems/ezpublish-kernel" to one of the "Resolving versions" mentioned above, or apply this patch manually:
https://github.com/ezsystems/ezpublish-kernel/commit/1551723ec134878a4cb598bfc5d900ba6164117a

## References
- https://github.com/ezsystems/ezpublish-kernel/commit/1551723ec134878a4cb598bfc5d900ba6164117a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezpublish-kernel/2018-11-21-1.yaml
- https://github.com/ezsystems/ezpublish-kernel
- https://web.archive.org/web/20210614181629/https://share.ez.no/community-project/security-advisories/ezsa-2018-008-rest-api-returns-list-of-all-siteaccesses
- http://share.ez.no/community-project/security-advisories/ezsa-2018-008-rest-api-returns-list-of-all-siteaccesses
