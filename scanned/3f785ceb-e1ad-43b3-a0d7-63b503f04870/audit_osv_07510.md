# [H] SQLite before 3.53.2 Heap Buffer Overflow via FTS5 fts5ChunkIterate

## Summary
Severity: High
Advisory: BIT-sqlite-2026-11824
Aliases: CVE-2026-11824
Ecosystem: Bitnami
Published: 2026-06-12
Source: https://osv.dev/vulnerability/BIT-sqlite-2026-11824
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=0 <3.53.2

## Details
SQLite before 3.53.2 contains a heap-based buffer overflow vulnerability in the FTS5 full-text search extension that allows attackers to cause a crash or execute arbitrary code by supplying a crafted database with malicious continuation page metadata specifying a szLeaf value smaller than 4. Attackers can trigger an integer underflow in fts5ChunkIterate() causing an inflated remaining byte count during FTS5 MATCH query processing, leading to a heap buffer overflow of attacker-controlled data in applications compiled with SQLITE_ENABLE_FTS5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-11824
- https://sqlite.org/releaselog/3_53_2.html
- https://sqlite.org/src/info/061febcf41ca
- https://sqlite.org/src/info/4a5ad516ea93
- https://www.vulncheck.com/advisories/sqlite-before-heap-buffer-overflow-via-fts5-fts5chunkiterate
