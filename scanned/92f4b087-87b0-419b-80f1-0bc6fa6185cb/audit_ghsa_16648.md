# [M] silverstripe/framework uploaded PHP script execution in assets

## Summary
Severity: Medium
Advisory: GHSA-f43j-8hq4-2xj9
CWE: CWE-20
Ecosystem: Packagist
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-f43j-8hq4-2xj9
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.4
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.1

## Details
A weakness in the .htaccess rules preventing requests to uploaded PHP scripts allows PHP scripts that had made their way into the assets directory to be successfully executed through the use of a specially crafted URL. There are protections in place to disallow upload of PHP scripts through the CMS, meaning this weakness does not lead to direct vulnerabilities.

In addition, sites hosted on the New Zealand Common Web Platform or SilverStripe Platform have additional configuration in place which prevents PHP script execution in assets, even in a malicious party manages to upload these into the folder.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/5b7eca2b6327556e2d5ad31bb00511b187e5992a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-012-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-012
