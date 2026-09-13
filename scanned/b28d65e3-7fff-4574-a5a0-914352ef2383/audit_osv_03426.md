# [C] ALPINE-CVE-2026-11822

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-11822
Ecosystem: Alpine:v3.23
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11822
Type: osv

## Affected
- Alpine:v3.23: `sqlite` — affected >=0 <3.53.4-r0

## Details
SQLite before 3.53.2 contains memory corruption vulnerabilities in the FTS5 full-text search extension that allow attackers to cause process crashes, memory exhaustion, or arbitrary code execution by supplying a crafted database with malformed FTS5 page data. Attackers can trigger an out-of-bounds read in fts5LeafSeek() via an attacker-controlled loop bound and a heap buffer overflow write in fts5ChunkIterate() through a crafted continuation page causing an integer underflow, exploitable when an FTS5 MATCH query is executed against the malicious database.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11822
