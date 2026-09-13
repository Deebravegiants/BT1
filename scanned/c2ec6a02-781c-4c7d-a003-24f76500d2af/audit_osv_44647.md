# [M] Checkmate through 3.11.0 Missing Authorization on Maintenance Window, Notification, and Check Deletion Routes

## Summary
Severity: Medium
Advisory: CVE-2026-85390
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-85390
Type: osv

## Details
Checkmate through 3.11.0 omits the isAllowed role guard middleware on maintenance-window, notification, and check-deletion routes, allowing read-only users to perform administrative actions. Attackers with user-role sessions can create arbitrary maintenance windows to silence alerts, modify notification channels, and delete monitor check history to erase incident evidence.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85390.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85390
- https://www.vulncheck.com/advisories/checkmate-through-3.11.0-missing-authorization-on-maintenance-window-notification-and-check-deletion-routes
- https://github.com/bluewave-labs/Checkmate/issues/3916
- https://github.com/bluewave-labs/Checkmate
- https://github.com/bluewave-labs/Checkmate/blob/v3.11.0/server/src/api/routes/checkRoutes.ts
- https://github.com/bluewave-labs/Checkmate/blob/v3.11.0/server/src/api/routes/maintenanceWindowRoutes.ts
- https://github.com/bluewave-labs/Checkmate/blob/v3.11.0/server/src/api/routes/notificationRoutes.ts
