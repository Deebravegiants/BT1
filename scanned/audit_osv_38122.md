# [C] OneUptime: Missing Authentication on Notification Endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-34758
Aliases: GHSA-q253-6wcm-h8hp
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34758
Type: osv

## Details
OneUptime is an open-source monitoring and observability platform. Prior to version 10.0.42, unauthenticated access to Notification test and Phone Number management endpoints allows SMS/Call/Email/WhatsApp abuse and phone number purchase. This issue has been patched in version 10.0.42.

## References
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34758.json
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-q253-6wcm-h8hp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34758
- https://github.com/OneUptime/oneuptime/commit/9adbd04538714740506708d6fa610e433be4d2a4
