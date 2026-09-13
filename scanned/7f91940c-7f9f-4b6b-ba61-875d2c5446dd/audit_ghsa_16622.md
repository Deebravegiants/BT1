# [H] eZ Publish Information disclosure in backend content tree menu

## Summary
Severity: High
Advisory: GHSA-cc2j-92jq-wgjg
CWE: CWE-200
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-cc2j-92jq-wgjg
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2011.0.0 <2017.8.1.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.4.0 <5.4.10.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.3.0 <5.3.12.2

## Details
This security advisory fixes an information disclosure vulnerability in the legacy admin content tree menu. If a view has been disabled in site.ini [SiteAccessRules] Rules, and an attacker accesses the backend with the URL to this module, then the tree menu may be displayed. Since the tree menu may contain hidden items, this may lead to information disclosure. We recommend that you install this Security Update as soon as possible.

To install, use Composer to update to one of the "Resolving versions" mentioned above, or apply this patch manually: https://github.com/ezsystems/ezpublish-legacy/commit/a4a0470f8d80f012fe14e4f8ab11c7d14375986c

## References
- https://github.com/ezsystems/ezpublish-legacy/commit/a4a0470f8d80f012fe14e4f8ab11c7d14375986c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezpublish-legacy/2017-09-11-1.yaml
- https://github.com/ezsystems/ezpublish-legacy
- http://share.ez.no/community-project/security-advisories/ezsa-2017-006-information-disclosure-in-backend-content-tree-menu
