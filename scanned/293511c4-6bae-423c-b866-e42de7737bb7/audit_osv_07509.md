# [H] SQLite before 3.53.2 Memory Corruption in FTS5 Extension

## Summary
Severity: High
Advisory: BIT-sqlite-2026-11822
Aliases: CVE-2026-11822
Ecosystem: Bitnami
Published: 2026-06-12
Source: https://osv.dev/vulnerability/BIT-sqlite-2026-11822
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=0 <3.53.2

## Details
SQLite before 3.53.2 contains memory corruption vulnerabilities in the FTS5 full-text search extension that allow attackers to cause process crashes, memory exhaustion, or arbitrary code execution by supplying a crafted database with malformed FTS5 page data. Attackers can trigger an out-of-bounds read in fts5LeafSeek() via an attacker-controlled loop bound and a heap buffer overflow write in fts5ChunkIterate() through a crafted continuation page causing an integer underflow, exploitable when an FTS5 MATCH query is executed against the malicious database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11822
- https://sqlite.org/releaselog/3_53_2.html
- https://sqlite.org/src/info/061febcf41ca
- https://sqlite.org/src/info/4a5ad516ea93
- https://www.vulncheck.com/advisories/sqlite-before-memory-corruption-in-fts5-extension
