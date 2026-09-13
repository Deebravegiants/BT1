# [M] Capgo - Unauthenticated Channel Enumeration and App Oracle via GET /channel_self

## Summary
Severity: Medium
Advisory: CVE-2026-56323
Aliases: GHSA-469v-6vw5-hxpq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-56323
Type: osv

## Details
Capgo before 12.128.2 contains an information disclosure vulnerability in the /functions/v1/channel_self endpoint that allows unauthenticated attackers to enumerate non-public channel names and determine app existence and subscription status. Remote attackers can send GET requests with arbitrary app_id parameters to disclose internal rollout channels, enumerate valid applications across tenants, and leak billing status without authentication or device binding.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56323.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-469v-6vw5-hxpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-56323
- https://www.vulncheck.com/advisories/capgo-unauthenticated-channel-enumeration-and-app-oracle-via-get-channel-self
