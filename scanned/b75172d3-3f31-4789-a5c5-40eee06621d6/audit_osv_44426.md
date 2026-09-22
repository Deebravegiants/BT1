# [M] Mastra Memory API Thread Ownership Check Is a No-op When mapUserToResourceId Is Unset

## Summary
Severity: Medium
Advisory: CVE-2026-82273
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82273
Type: osv

## Details
Mastra through 1.63.0 contains an authentication bypass vulnerability in the memory API thread ownership validation when mapUserToResourceId callback is omitted from configuration. Authenticated attackers can enumerate all threads via GET /api/memory/threads and read conversation history and metadata of other resource owners.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82273.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82273
- https://www.vulncheck.com/advisories/mastra-memory-api-thread-ownership-check-is-a-no-op-when-mapusertoresourceid-is-unset
- https://github.com/mastra-ai/mastra/issues/18911
- https://github.com/mastra-ai/mastra
- https://github.com/mastra-ai/mastra/blob/b7e66f0c478a227985e0062794ef058c3714fabf/packages/server/src/server/handlers/utils.ts
