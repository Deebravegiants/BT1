# [C] Missing warning can lead to unauthenticated admin access in SilverStripe

## Summary
Severity: Critical
Advisory: GHSA-cg8j-8w52-735v
CVE: CVE-2019-12204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-11-12
Source: https://github.com/advisories/GHSA-cg8j-8w52-735v
Type: github-advisory

## Affected
- Packagist: `silverstripe/cms` — affected >=4.4.0 <4.4.4
- Packagist: `silverstripe/framework` — affected >=4.1.0 <4.3.5

## Details
In SilverStripe through 4.3.3, a missing warning about leaving install.php in a public webroot can lead to unauthenticated admin access.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12204
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2019-12204.yaml
- https://packagist.org/packages/silverstripe/cms
- https://packagist.org/packages/silverstripe/framework
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/CVE-2019-12204
- https://www.silverstripe.org/download/security-releases/cve-2019-12204
