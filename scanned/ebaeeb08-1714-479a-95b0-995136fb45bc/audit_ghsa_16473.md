# [M] silverstripe/framework's URL parameters `isDev` and `isTest` unguarded

## Summary
Severity: Medium
Advisory: GHSA-55qg-6c4m-mw6g
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-55qg-6c4m-mw6g
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.4
- Packagist: `silverstripe/framework` — affected >=4.1.0rc1 <4.1.1

## Details
The URL parameters `isDev` and `isTest` are accessible to unauthenticated users who access a SilverStripe website or application. This allows unauthorised users to expose information that is usually hidden on production environments such as verbose errors (including backtraces) and other debugging tools only available to sites running in "dev mode". Core functionality does not expose user data through these methods. Depending on your website configuration, community modules might have added more specific functionality which can be used to either access or alter user data.

We have fixed the usage of isDev and isTest in SilverStripe 4.x, and removed the URL parameters in the next major release of SilverStripe.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/d935140a9528a3a42323b51d84fb2bcd3da065a7
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2018-005-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2018-005
