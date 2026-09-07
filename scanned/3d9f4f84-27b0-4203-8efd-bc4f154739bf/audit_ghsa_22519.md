# [H] SilverStripe Folders migrated from 3.x may be unsafe to upload to

## Summary
Severity: High
Advisory: GHSA-592m-4533-rxq9
CVE: CVE-2020-9280
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-592m-4533-rxq9
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0 <4.4.6
- Packagist: `silverstripe/userforms` — affected >=5.0.0 <5.4.2
- Packagist: `silverstripe/assets` — affected >=1.0.0 <1.4.7
- Packagist: `silverstripe/assets` — affected >=1.5.0 <1.5.2

## Details
In SilverStripe through 4.5, files uploaded via Forms to folders migrated from Silverstripe CMS 3.x may be put to the default "/Uploads" folder instead. This affects installations which allowed upload folder protection via the optional silverstripe/secureassets module under 3.x. This module is installed and enabled by default on the Common Web Platform (CWP). The vulnerability only affects files uploaded after an upgrade to 4.x.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9280
- https://github.com/silverstripe/silverstripe-assets/commit/6779fd3c8c1c05a3db5035bf6e541c9483d161fc
- https://github.com/silverstripe/silverstripe-userforms/commit/3bbad2044279ade5e5a5d0ae1822bafe479f8a26
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/assets/CVE-2020-9280.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2020-9280
