# [M] SilverStripe Vulnerability on 'isDev', 'isTest' and 'flush' $_GET validation

## Summary
Severity: Medium
Advisory: GHSA-g4hp-pfvf-vm5w
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-g4hp-pfvf-vm5w
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.0.0 <3.0.14
- Packagist: `silverstripe/framework` — affected >=3.1.0 <3.1.13

## Details
When a secure token parameter is provided to a SilverStripe site (such as isDev or flush) an empty token parameter can be provided in order to bypass normal authentication parameters.

For instance, http://www.mysite.com/?isDev=1&isDevtoken will force a site to dev mode. Alternatively, "flush" could also be used in succession to cause excessive load on a victim site and risk denial of service.

The fix in this case is to ensure that empty tokens fail the validation check.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/a978b891e13d22dddee7e0735a7032f13964447d
- https://github.com/silverstripe/silverstripe-framework/commit/cb6717c3f85753bdc30087f280720c6d3f639ff3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2015-014-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/software/download/security-releases/ss-2015-014
