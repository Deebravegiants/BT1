# [C] mem0 - OpenMemory API Unauthenticated Access via Memory Endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-59705
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-59705
Type: osv

## Details
mem0's openmemory/api component contains an unauthenticated access vulnerability that allows unauthenticated attackers to read, write, and delete arbitrary user memories by accessing API routers registered without authentication middleware. Attackers can supply arbitrary user_id parameters or directly access memory retrieval endpoints to expose private memory content, or invoke pause endpoints with global_pause=true to cause denial-of-service across all users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59705.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59705
- https://www.vulncheck.com/advisories/mem0-openmemory-api-unauthenticated-access-via-memory-endpoints
- https://github.com/mem0ai/mem0/issues/6080
- https://github.com/mem0ai/mem0/commit/a3154d59e52386d4e1189c1f5f44819868f76514
- https://github.com/mem0ai/mem0
