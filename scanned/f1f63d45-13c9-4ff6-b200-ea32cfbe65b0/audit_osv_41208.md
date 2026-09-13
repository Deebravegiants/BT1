# [M] NATS Server: `no_auth_user` pre-CONNECT fast path bypasses user connection restrictions

## Summary
Severity: Medium
Advisory: CVE-2026-58211
Aliases: GHSA-hmmp-q8cx-v964
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-58211
Type: osv

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.3 and 2.12.12, a client could be registered as the configured no_auth_user through a parser path used when the first client operation was not CONNECT, bypassing user-level connection restrictions such as allowed_connection_types or proxy_required that normal authentication would apply. This issue is fixed in versions 2.14.3 and 2.12.12.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58211.json
- https://github.com/nats-io/nats-server/security/advisories/GHSA-hmmp-q8cx-v964
- https://nvd.nist.gov/vuln/detail/CVE-2026-58211
