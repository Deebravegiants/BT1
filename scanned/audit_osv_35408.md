# [M] stoatchat before 20250210-1 Unrestricted Message History Fetch

## Summary
Severity: Medium
Advisory: CVE-2025-71377
Aliases: GHSA-h7h6-7pxm-mc66
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2025-71377
Type: osv

## Details
stoatchat (delta) versions before 20250210-1 (0.8.2) contain a logic error in the query messages route. When fetching messages 'nearby' another message, the database query can be given a message limit of zero, which the database interprets as 'no limit'. A remote unauthenticated attacker can craft nearby message fetch requests to download an entire channel's message history in a single expensive request, and can send many such requests in parallel, resulting in denial of service through resource exhaustion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71377.json
- https://github.com/stoatchat/stoatchat/security/advisories/GHSA-h7h6-7pxm-mc66
- https://nvd.nist.gov/vuln/detail/CVE-2025-71377
- https://www.vulncheck.com/advisories/stoatchat-before-20250210-1-unrestricted-message-history-fetch
- https://github.com/stoatchat/stoatchat/commit/5f84daa9dba34c103cd83a2ee1f5e5ba900bfe94
