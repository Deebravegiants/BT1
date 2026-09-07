# [H] eZ Publish Legacy Patch EZSA-2018-001 for Several vulnerabilities

## Summary
Severity: High
Advisory: GHSA-82rv-45pc-v28w
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-82rv-45pc-v28w
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezpublish-legacy` — affected >=2011.0.0 <2017.12.2.1
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.4.0 <5.4.11.3
- Packagist: `ezsystems/ezpublish-legacy` — affected >=5.3.0 <5.3.12.3

## Details
This security advisory fixes 4 separate vulnerabilities in eZ Publish Legacy, and we recommend that you install it as soon as possible if you are using Legacy by itself or via the LegacyBridge.
 
First, it increases the randomness, and thus the security, of the pseudo-random bytes used to generate a hash for the "forgot password" feature. This protects accounts against being taken over through attacks trying to predict the hash. If the increased randomness is not available in your PHP installation, it will now log a warning.
 
Second, it improves security of the information collector feature, by ensuring no collection emails will be sent from invalid manipulated forms.
 
Third, it stops the possible leaking of the names of content objects that should not be readable for certain users, on installations where these users can create or edit XML text.
 
Fourth, it protects against cross-site scripting (XSS) in the Matrix data type, on installations where users are allowed to edit content classes / content types.

We recommend that you install the security update as soon as possible.

To install, use Composer to update to one of the "Resolving versions" mentioned above, or apply these patches manually:
https://github.com/ezsystems/ezpublish-legacy/commit/917711eb7ffe2b52a3e9fe12505f6810a63696f7
https://github.com/ezsystems/ezpublish-legacy/commit/6db0e6b7739481f27d954548388bd3f0ed2c6fdd
https://github.com/ezsystems/ezpublish-legacy/commit/efcd2b61b15eaaf74e0ff28d6c723cf28e655dab
https://github.com/ezsystems/ezpublish-legacy/commit/f9ffaf590b63b4f552142cfd4441afbbfb3f19b1

## References
- https://github.com/ezsystems/ezpublish-legacy/commit/6db0e6b7739481f27d954548388bd3f0ed2c6fdd
- https://github.com/ezsystems/ezpublish-legacy/commit/917711eb7ffe2b52a3e9fe12505f6810a63696f7
- https://github.com/ezsystems/ezpublish-legacy/commit/efcd2b61b15eaaf74e0ff28d6c723cf28e655dab
- https://github.com/ezsystems/ezpublish-legacy/commit/f9ffaf590b63b4f552142cfd4441afbbfb3f19b1
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezpublish-legacy/2018-02-26-1.yaml
- https://github.com/ezsystems/ezpublish-legacy
- https://web.archive.org/web/20210614192631/http://share.ez.no/community-project/security-advisories/ezsa-2018-001-several-vulnerabilities-in-forgot-password-information-collector-xml-text-and-matrix-field-type-features
