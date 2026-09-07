# [M] eZ Publish Legacy Cross-site Scripting (XSS) in 'disabled module' error template

## Summary
Severity: Medium
Advisory: GHSA-2vh3-cj9j-mcj5
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-2vh3-cj9j-mcj5
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2018.9.0 <2018.9.1.2
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2018.6.0 <2018.6.1.3
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2011.0.0 <2017.12.4.2
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.4.0 <5.4.12.2
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.3.0 <5.3.12.5

## Details
This security advisory fixes a vulnerability in eZ Publish Legacy, and we recommend that you install it as soon as possible if you are using Legacy via the LegacyBridge.

Installations where all modules are disabled may be vulnerable to XSS injection in the module name. This is a rare configuration, but we still recommend installing the update, which adds the necessary input washing.

To install, use Composer to update to one of the "Resolving versions" mentioned above, or apply this patch manually:
https://github.com/ezsystems/ezpublish-legacy/commit/4697bff700e8cf95d5847ea19dad3479a77b02d9

## References
- https://github.com/ezsystems/ezpublish-legacy/commit/4697bff700e8cf95d5847ea19dad3479a77b02d9
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezpublish-legacy/2018-11-01-1.yaml
- https://github.com/ezsystems/ezpublish-legacy
- https://web.archive.org/web/20210614172734/http://share.ez.no/community-project/security-advisories/ezsa-2018-006-xss-vulnerability-in-disabled-module-error-template
- http://share.ez.no/community-project/security-advisories/ezsa-2018-006-xss-vulnerability-in-disabled-module-error-template
