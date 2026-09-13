# [C] Odysseus Missing Admin Authorization via Embedding Endpoint Routes

## Summary
Severity: Critical
Advisory: CVE-2026-70619
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-70619
Type: osv

## Details
Odysseus before commit bf325f6 contains a missing authorization vulnerability that allows authenticated non-admin users to manage server-wide embedding backend configuration by invoking endpoint management routes that verify session authentication but omit the admin authorization guard. Attackers can supply an attacker-controlled URL to overwrite the embedding backend persisted in the endpoint configuration file and process environment, causing all subsequent embedding operations including chat messages, RAG queries, memory entries, and vault text to be transmitted in plaintext to the attacker-controlled destination, or delete the endpoint configuration to deny embedding service to all users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70619.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70619
- https://www.vulncheck.com/advisories/odysseus-missing-admin-authorization-via-embedding-endpoint-routes
- https://github.com/odysseus-dev/odysseus/issues/80
- https://github.com/odysseus-dev/odysseus/commit/bf325f6b2185cb42bc5d8f5713a64aecffb766d4
- https://github.com/odysseus-dev/odysseus
- https://aydinnyunus.github.io/2026/06/16/odysseus-embedding-endpoint-takeover/
- https://github.com/odysseus-dev/odysseus/issues/132
