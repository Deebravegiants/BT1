# [M] Silverstripe HtmlEditor embed url sanitisation

## Summary
Severity: Medium
Advisory: GHSA-qp29-wcc2-vmpc
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-qp29-wcc2-vmpc
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.0.0 <3.2.1

## Details
"Add from URL" doesn't clearly sanitise URL server side

HtmlEditorField_Toolbar has an action HtmlEditorField_Toolbar#viewfile, which gets called by the CMS when adding a media "from a URL" (i.e. via oembed).

This action gets the URL to add in the GET parameter FileURL. However it doesn't do any URL sanitising server side. The current logic will pass this through to Oembed, which will probably reject most dangerous URLs, but it's possible future changes would break this.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-027-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2015-027
