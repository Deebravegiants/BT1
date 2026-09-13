# [M] OpenCTI's GraphQL IDOR enables authenticated users to modify or delete notifications of other users

## Summary
Severity: Medium
Advisory: CVE-2025-46732
Aliases: GHSA-535g-qp2c-h7vp, PYSEC-2025-181
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-07-18
Source: https://osv.dev/vulnerability/CVE-2025-46732
Type: osv

## Details
OpenCTI is an open source platform for managing cyber threat intelligence knowledge and observables. Prior to version 6.6.6, an IDOR vulnerability in the GrapQL `NotificationLineNotificationMarkReadMutation` and `NotificationLineNotificationDeleteMutation` mutations of OpenCTI allows an authenticated user to change the read status of a notification or delete a notification of another user in case he has knowledge of the UUID of the notification. When changing the read status of a notification, the user also receives the content of the notification they changed the read status of. Authenticated Users in OpenCTI can read, modify and delete notification of other users if they know the UUID of the notification. Version 6.6.6 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46732.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-535g-qp2c-h7vp
- https://nvd.nist.gov/vuln/detail/CVE-2025-46732
