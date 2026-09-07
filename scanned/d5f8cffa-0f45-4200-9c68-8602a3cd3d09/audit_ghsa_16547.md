# [H] Silverstripe SiteTree Creation Permission Vulnerability

## Summary
Severity: High
Advisory: GHSA-3mm9-2p44-rw39
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-05-22
Source: https://github.com/advisories/GHSA-3mm9-2p44-rw39
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=3.0.0 <3.0.12
- Packagist: `silverstripe/cms` — affected >=3.1.0 <3.1.11

## Details
A vulnerability exists in the permission validation for SiteTree object creation. By default user permissions are not validated by the SiteTree::canCreate method, unless overridden by user code or via the configuration system.

This vulnerability will allow users, or unauthenticated guests, to create new SiteTree objects in the database. This vulnerability is present when such users are given CMS access via other means, or if there is another mechanism (such as RestfulServer module) which allows model editing and relies on model-level permission checks.

This vulnerability is restricted to the creation of draft or live pages, and does not allow users to edit, publish, or unpublish existing pages.

All users should upgrade as soon as possible.

## References
- https://github.com/silverstripe/silverstripe-cms/commit/3df41e1176385215f15fffb04fcba033a5151fb4
- https://github.com/silverstripe/silverstripe-cms/commit/64955e57d1239975183f47d3ac8c3e801ddbf122
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/cms/SS-2015-008-1.yaml
- https://github.com/silverstripe/silverstripe-cms
- https://www.silverstripe.org/software/download/security-releases/ss-2015-008-sitetree-creation-permission-vulnerability
