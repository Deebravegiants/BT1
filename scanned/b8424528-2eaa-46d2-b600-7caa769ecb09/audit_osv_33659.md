# [M] wire-webapp Has Insufficient Session Invalidation after User Logout

## Summary
Severity: Medium
Advisory: CVE-2025-48061
Aliases: GHSA-7r6m-qjwm-w44q
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-05-22
Source: https://osv.dev/vulnerability/CVE-2025-48061
Type: osv

## Details
wire-webapp is the web application for the open-source messaging service Wire. A change caused a regression resulting in sessions not being properly invalidated. A user that logged out of the Wire webapp, could have been automatically logged in again after re-opening the application. This does not happen when the user is logged in as a temporary user by selecting "This is a public computer" during login or the user selects "Delete all your personal information and conversations on this device" upon logout. The underlying issue has been fixed with wire-webapp version 2025-05-20-production.0. As a workaround, this behavior can be prevented by either deleting all information upon logout as well as logging in as a temporary client.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48061.json
- https://github.com/wireapp/wire-webapp/security/advisories/GHSA-7r6m-qjwm-w44q
- https://nvd.nist.gov/vuln/detail/CVE-2025-48061
