# [M] Unauthenticated authorize requests create unbounded, never-expiring CIMD client rows and cache entries in ash_authentication_oauth2_server

## Summary
Severity: Medium
Advisory: CVE-2026-82753
Aliases: EEF-CVE-2026-82753, GHSA-9pv3-wxjm-f846
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-82753
Type: osv

## Details
Allocation of Resources Without Limits or Throttling vulnerability in ash-project ash_authentication_oauth2_server allows an unauthenticated attacker to exhaust database storage and memory.

The /authorize endpoint is unauthenticated by design. With Client ID Metadata Documents enabled, resolve_client/3 in AshAuthentication.Oauth2Server.CIMD fetches the document for each new URL-shaped client_id and upserts a client row, with no cap on the number of rows, no expiry or garbage collection, and no length bound on the fetched fields; the document was also placed in CIMD.Cache before validation, so even rejected documents held cache memory until their TTL. An attacker serving valid documents at many distinct URLs creates one permanent client row per URL, each able to carry multi-megabyte strings, growing storage and memory without bound.

This issue affects ash_authentication_oauth2_server: from 0.3.0 before 0.3.1.

## References
- https://cna.erlef.org/cves/CVE-2026-82753.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82753
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82753.json
- https://github.com/ash-project/ash_authentication_oauth2_server/security/advisories/GHSA-9pv3-wxjm-f846
- https://nvd.nist.gov/vuln/detail/CVE-2026-82753
- https://github.com/ash-project/ash_authentication_oauth2_server/commit/45e24f69e0f95d67413e2508acc2264156acb5ac
- https://github.com/ash-project/ash_authentication_oauth2_server
