# [H] silverstripe/framework SQL injection in full text search 

## Summary
Severity: High
Advisory: GHSA-xx4r-5265-48j6
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-xx4r-5265-48j6
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.5.0-rc1 <3.5.6
- Packagist: `silverstripe/framework` — affected >=3.6.0-rc1 <3.6.3
- Packagist: `silverstripe/framework` — affected >=4.0.0-rc1 <4.0.1

## Details
When performing a fulltext search in SilverStripe 4.0.0 the 'start' querystring parameter is never escaped safely. This exposes a possible SQL injection vulnerability.

The issue exists in 3.5 and 3.6 but is less vulnerable, as SearchForm sanitises these variables prior to passing to mysql.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/099a5a3c2d99ed39bdd8815e1e2790bb9351770b
- https://github.com/silverstripe/silverstripe-framework/commit/a8465900bdc77199176c953890ce7587045b1ea4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2017-008-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2017-008
