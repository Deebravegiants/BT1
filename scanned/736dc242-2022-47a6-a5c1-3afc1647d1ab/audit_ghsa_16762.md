# [H] silverstripe/framework allows upload of dangerous file types

## Summary
Severity: High
Advisory: GHSA-vcg6-8fxc-x5cq
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-vcg6-8fxc-x5cq
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.6.5-rc1 <3.6.6
- Packagist: `silverstripe/framework` — affected >=4.0.3-rc1 <4.0.4
- Packagist: `silverstripe/framework` — affected >=4.1.0-rc1 <4.1.1

## Details
Some potentially dangerous file types exist in File.allowed_extensions which could allow a malicious CMS user to upload files that then get executed in the security context of the website. We have removed the ability to upload .css, .js, .potm, .dotm, .xltm and .jar files in the default configuration. Since allowed_extensions are synced to webserver configuration (in assets/.htaccess) automatically, this will also deny access to any existing uploads with these extensions.

Review our security guidelines for the Common Web Platform and the File Security guide for SilverStripe 4 to find out how to add or remove extensions.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/0408048653fafc52e02b4dbc6288e14e634ac613
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-014-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-014
