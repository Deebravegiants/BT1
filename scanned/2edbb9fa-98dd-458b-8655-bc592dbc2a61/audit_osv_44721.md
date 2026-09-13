# [M] Chroma 1.5.9 Unbounded HNSW Index Parameters Memory Exhaustion

## Summary
Severity: Medium
Advisory: CVE-2026-85664
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85664
Type: osv

## Details
Chroma 1.5.9 fails to validate maximum bounds on HNSW index parameters max_neighbors, ef_construction, and ef_search in collection-create requests. Unauthenticated attackers can supply arbitrarily large parameter values to exhaust server memory and cause denial of service during index compaction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85664.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85664
- https://www.vulncheck.com/advisories/chroma-1.5.9-unbounded-hnsw-index-parameters-memory-exhaustion
- https://github.com/chroma-core/chroma/issues/7225
- https://github.com/chroma-core/chroma
- https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/src/auth/mod.rs
- https://github.com/chroma-core/chroma/blob/1.5.9/rust/types/src/hnsw_configuration.rs
