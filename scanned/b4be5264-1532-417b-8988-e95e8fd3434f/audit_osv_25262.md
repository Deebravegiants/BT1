# [H] Insufficiently Protected ChatBot Credentials in tgstation-server

## Summary
Severity: High
Advisory: CVE-2023-32687
Aliases: GHSA-rv76-495p-g7cp
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-05-29
Source: https://osv.dev/vulnerability/CVE-2023-32687
Type: osv

## Details
tgstation-server is a toolset to manage production BYOND servers. Starting in version 4.7.0 and prior to 5.12.1, instance users with the list chat bots permission can read chat bot connections strings without the associated permission. This issue is patched in version 5.12.1. As a workaround, remove the list chat bots permission from users that should not have the ability to view connection strings. Invalidate any credentials previously stored for safety.

## References
- https://github.com/tgstation/tgstation-server/releases/tag/tgstation-server-v5.12.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32687.json
- https://github.com/tgstation/tgstation-server/security/advisories/GHSA-rv76-495p-g7cp
- https://nvd.nist.gov/vuln/detail/CVE-2023-32687
- https://github.com/tgstation/tgstation-server/pull/1487
