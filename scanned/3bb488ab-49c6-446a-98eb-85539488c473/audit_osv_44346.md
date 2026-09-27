# [M] OpenRemote before 1.28.0 Cross-Realm Information Disclosure via Notification API

## Summary
Severity: Medium
Advisory: CVE-2026-81679
Aliases: GHSA-6ff4-4frc-r287
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81679
Type: osv

## Details
OpenRemote versions before 1.28.0 contain a cross-realm information disclosure vulnerability in the Notification REST API that allows per-realm tenant administrators to read all tenants' sent notifications including message bodies. Attackers with read:admin credentials in one realm can submit a zero-parameter GET request to the notification endpoint to retrieve sensitive notification metadata and message content from all realms.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81679.json
- https://github.com/openremote/openremote/security/advisories/GHSA-6ff4-4frc-r287
- https://nvd.nist.gov/vuln/detail/CVE-2026-81679
- https://www.vulncheck.com/advisories/openremote-before-1.28.0-cross-realm-information-disclosure-via-notification-api
