# [M] silverstripe/framework missing ACL on reports

## Summary
Severity: Medium
Advisory: GHSA-52cx-hpc5-cxwc
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-27
Source: https://github.com/advisories/GHSA-52cx-hpc5-cxwc
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=3.1.19-rc1 <3.1.20
- Packagist: `silverstripe/framework` — affected >=3.2.4-rc1 <3.2.5
- Packagist: `silverstripe/framework` — affected >=3.3.2-rc1 <3.3.3
- Packagist: `silverstripe/framework` — affected >=3.4.0-rc1 <3.4.1

## Details
The SS_Report, and the reports CMS section only checks `canView()` when listing the reports that can be viewed by the current user.

It does not (and should) perform `canView` checks when the report is actually viewed, so if you know the URL to a report and can otherwise access the Reports section of the CMS, you can view any report.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-012-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-012
