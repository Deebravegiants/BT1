# [M] eZ Platform Bundled jQuery affected by CVE-2019-11358

## Summary
Severity: Medium
Advisory: GHSA-jrpw-8884-2747
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-jrpw-8884-2747
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-admin-ui-assets` — affected >=4.0.0 <4.2.0

## Details
In eZ Platform 2.x, ezsystems/ezplatform-admin-ui-assets before v4.2.0 includes jQuery version 3.3.1. This version of jQuery is affected by the security vulnerability https://www.cvedetails.com/cve/CVE-2019-11358/
This is fixed in jQuery version 3.4. We recommend that you upgrade your ezsystems/ezplatform-admin-ui-assets to v4.2.0 using Composer. This release includes jQuery 3.4.1.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezplatform-admin-ui-assets/2019-07-04-1.yaml
- https://github.com/ezsystems/ezplatform-admin-ui-assets
- https://share.ez.no/community-project/security-advisories/ezsa-2019-005-bundled-jquery-affected-by-cve-2019-11358
- https://web.archive.org/web/20210614184115/https://share.ez.no/community-project/security-advisories/ezsa-2019-005-bundled-jquery-affected-by-cve-2019-11358
