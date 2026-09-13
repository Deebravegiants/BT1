# [C] OneUptime: Unauthenticated notification API endpoints - financial abuse via phone number purchase, service disruption, and SMTP credential exposure

## Summary
Severity: Critical
Advisory: CVE-2026-34759
Aliases: GHSA-6wc5-rhvj-cx7f
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34759
Type: osv

## Details
OneUptime is an open-source monitoring and observability platform. Prior to version 10.0.42, multiple notification API endpoints are registered without authentication middleware, while sibling endpoints in the same codebase correctly use ClusterKeyAuthorization.isAuthorizedServiceMiddleware. These endpoints are externally reachable via the Nginx proxy at /notification/. Combined with a projectId leak from the public Status Page API, an unauthenticated attacker can purchase phone numbers on the victim's Twilio account and delete all existing alerting numbers. This issue has been patched in version 10.0.42.

## References
- https://github.com/OneUptime/oneuptime/releases/tag/10.0.42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34759.json
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-6wc5-rhvj-cx7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-34759
- https://github.com/OneUptime/oneuptime/commit/9adbd04538714740506708d6fa610e433be4d2a4
