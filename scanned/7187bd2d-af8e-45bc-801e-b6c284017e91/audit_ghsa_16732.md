# [H] Cross-site Scripting in eZFind spellcheck

## Summary
Severity: High
Advisory: GHSA-9cq2-pcgr-8h62
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-9cq2-pcgr-8h62
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezfind-ls` — affected >=2017.12.0 <2017.12.0.1
- Packagist: `ezsystems/ezfind-ls` — affected >=5.4.0 <5.4.11.1
- Packagist: `ezsystems/ezfind-ls` — affected >=5.3.0 <5.3.6.1

## Details
This security advisory fixes a vulnerability in the legacy eZ Find extension, which can be used with the LegacyBridge in eZ Platform. It affects sites using the "Did you mean...?" spell check / search suggestion feature. This feature is vulnerable to Cross-site Scripting (XSS) injection (reflected XSS). The update adds the necessary escaping of injected code. If you're affected, we recommend that you install it as soon as possible.
 
If you have custom search templates, please make sure you update these as well. Ensure that "search_extras.spellcheck_collation" is followed by the "wash" operator, like this:
{$search_extras.spellcheck_collation|wash}
 
To install, use Composer to update to one of the "Resolving versions" mentioned above, or apply this patch manually:
https://github.com/ezsystems/ezfind/commit/51c17ea9b1231c20db8221f34d01c649060f1e91

## References
- https://github.com/ezsystems/ezfind/commit/51c17ea9b1231c20db8221f34d01c649060f1e91
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezfind-ls/2019-05-23-1.yaml
- https://github.com/ezsystems/ezfind
- https://share.ez.no/community-project/security-advisories/ezsa-2019-003-xss-in-ezfind-spellcheck
- https://web.archive.org/web/20210614183107/https://share.ez.no/community-project/security-advisories/ezsa-2019-003-xss-in-ezfind-spellcheck
