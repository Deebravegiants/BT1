# [M] Craft CMS 5.0.0-RC1 before 5.10.12 Permission Escalation via UsersController

## Summary
Severity: Medium
Advisory: CVE-2026-86731
Aliases: GHSA-jqf5-vfg6-8cx5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86731
Type: osv

## Details
Craft CMS versions 5.0.0-RC1 through 5.10.11 are missing an admin-target guard in UsersController::actionActivateUser (the users/activate-user action). While the action requires the administrateUsers permission, it does not call requireAdmin() when the targeted user is an administrator, unlike the mirror action actionDeactivateUser. As a result, an authenticated control panel user who is not an administrator but holds the administrateUsers permission can activate a pending or deliberately deactivated administrator account, which can lead to permission escalation when combined with resetting that account's password. The issue is fixed in Craft CMS 5.10.12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86731.json
- https://github.com/craftcms/cms/security/advisories/GHSA-jqf5-vfg6-8cx5
- https://nvd.nist.gov/vuln/detail/CVE-2026-86731
- https://www.vulncheck.com/advisories/craft-cms-5.0.0-rc1-before-5.10.12-permission-escalation-via-userscontroller
