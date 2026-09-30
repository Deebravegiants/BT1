# [C] LightRAG: Missing Authentication for Critical API Functions in Default Configuration

## Summary
Severity: Critical
Advisory: CVE-2026-61808
Aliases: GHSA-mmg5-8x8q-v934
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-61808
Type: osv

## Details
LightRAG provides simple and fast retrieval-augmented generation. Through version 1.5.4, the LightRAG API server binds to all network interfaces with authentication disabled by default, allowing an unauthenticated network attacker to read indexed document content, upload or delete documents, modify the knowledge graph, cancel pipelines, clear caches, and consume LLM resources. This issue is mitigated in version 1.5.5rc1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61808.json
- https://github.com/HKUDS/LightRAG/security/advisories/GHSA-mmg5-8x8q-v934
- https://nvd.nist.gov/vuln/detail/CVE-2026-61808
- https://github.com/HKUDS/LightRAG/commit/0bd102401b4b28a02664e5b6af476bf7a4470292
