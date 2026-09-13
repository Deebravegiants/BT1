# [M] SiYuan before v3.8.2 Unbounded Memory Consumption via ControlConcurrency

## Summary
Severity: Medium
Advisory: CVE-2026-85585
Aliases: GHSA-p59v-3q54-qq55
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85585
Type: osv

## Details
SiYuan before v3.8.2 contains an unbounded resource consumption vulnerability in the request-concurrency middleware that retains mutex entries for every unique request path without eviction. Unauthenticated attackers can send numerous unique request paths to permanently increase process memory and synchronization overhead, degrading availability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85585.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-p59v-3q54-qq55
- https://nvd.nist.gov/vuln/detail/CVE-2026-85585
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-unbounded-memory-consumption-via-controlconcurrency
