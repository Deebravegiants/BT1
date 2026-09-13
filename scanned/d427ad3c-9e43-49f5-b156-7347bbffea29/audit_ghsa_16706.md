# [H] eZ Platform Object Injection in SiteAccessMatchListener

## Summary
Severity: High
Advisory: GHSA-2w9p-xxqr-h253
CWE: CWE-94
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-2w9p-xxqr-h253
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-kernel` — affected >=1.0.0 <1.0.3

## Details
This Security Advisory is about an object injection vulnerability in the SiteAccessMatchListener of eZ Platform, which could lead to remote code execution (RCE), a very serious threat. All sites may be affected.

Update: There are bugs introduced by this fix, particularly but not limited to compound siteaccess matchers. These have been fixed in ezsystems/ezplatform-kernel v1.0.3, and in ezsystems/ezpublish-kernel v7.5.8, v6.13.6.4, and v5.4.15.

## References
- https://ezplatform.com/security-advisories/ezsa-2020-004-object-injection-in-siteaccessmatchlistener
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezplatform-kernel/2020-05-20-1.yaml
- https://github.com/ezsystems/ezplatform-kernel
- https://web.archive.org/web/20201024030303/https://ezplatform.com/security-advisories/ezsa-2020-004-object-injection-in-siteaccessmatchlistener
