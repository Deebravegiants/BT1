# [M] FreeScout IDOR Vulnerability: PERM_EDIT_USERS allows modifying any user's notification subscriptions (incomplete fix of CVE-2025-48472)

## Summary
Severity: Medium
Advisory: CVE-2026-41903
Aliases: GHSA-f489-qxv6-gvgg
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-41903
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.217, a user holding the PERM_EDIT_USERS permission (intended for general user-profile editing) can read and modify the notification subscriptions of any other user, including admins, by sending a single POST request. This is a sibling of CVE-2025-48472's notification authorization bypass — the prior fix did not cover this code path. A non-admin attacker can silently disable an admin's email/browser/mobile notifications, suppressing security alerts and conversation-assignment notices. This issue has been patched in version 1.8.217.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.217
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41903.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-f489-qxv6-gvgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-41903
