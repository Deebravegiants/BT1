# [M] SilverStripe CMS Cross-site Scripting vulnerabilities inherited from TinyMCE

## Summary
Severity: Medium
Advisory: GHSA-jxcx-3h54-qqxx
CWE: CWE-79
Ecosystem: Packagist
Published: 2023-08-23
Source: https://github.com/advisories/GHSA-jxcx-3h54-qqxx
Type: github-advisory

## Affected
- Packagist: `silverstripe/admin` — affected >=1.0.0 <1.13.6

## Details
TinyMCE 4.x is vulnerable to several XSS vectors, which had been patched in later versions. Two of these have been identified as affecting silverstripe/admin.

Only Silverstripe CMS 4 is affected by these vulnerabilities. It's not possible to upgrade Silverstripe CMS 4 to use a more recent release of TinyMCE without introducing breaking changes. Instead, the security patches that shipped in later releases of TinyMCE have been backported to the TinyMCE version bundled in silverstripe/admin.

Silverstripe CMS 5 is not affected by these vulnerabilities because it uses TinyMCE 6.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/admin/SS-2023-002.yaml
- https://github.com/silverstripe/silverstripe-admin
- https://www.silverstripe.org/download/security-releases/SS-2023-002
