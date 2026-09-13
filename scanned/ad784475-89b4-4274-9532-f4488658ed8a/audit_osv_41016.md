# [C] Maxun < 0.0.42 - Cross-Tenant IDOR in Storage and Webhook API Handlers

## Summary
Severity: Critical
Advisory: CVE-2026-56767
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-56767
Type: osv

## Details
Maxun before 0.0.42 contains a cross-tenant insecure direct object reference vulnerability in storage and webhook API handlers that allows authenticated users to access other users' robots and OAuth tokens. Attackers can read plaintext Google and Airtable access tokens, modify, delete, or execute other users' robots by bypassing ownership checks in API endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56767.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56767
- https://www.vulncheck.com/advisories/maxun-cross-tenant-idor-in-storage-and-webhook-api-handlers
- https://github.com/getmaxun/maxun/pull/1088
- https://github.com/getmaxun/maxun/commit/11db0257531f1c23dec94727793c9444ee2873cf
- https://github.com/getmaxun/maxun
- https://github.com/getmaxun/maxun/issues/1079
