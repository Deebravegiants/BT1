# [M] TimescaleDB 2.29.1 Out-of-Bounds Read DoS via Bulk Dictionary Decompression Negative Index

## Summary
Severity: Medium
Advisory: CVE-2026-70635
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70635
Type: osv

## Details
TimescaleDB through 2.29.1, fixed in commit 517c13e, contains an out-of-bounds read vulnerability that allows authenticated attackers to cause query-result integrity failures or backend crashes by supplying a crafted Simple8b selector-11 value, which is stored in the signed int16 Arrow dictionary-index type and bypasses index validation checks in bulk text dictionary decompression. Attackers with direct DML access to a non-frozen physical compressed hypertable relation can trigger an out-of-bounds read before the base of the live offsets array through the VectorAgg single-text hashing strategy, resulting in incorrect aggregation output, backend SIGSEGV, or PostgreSQL crash recovery depending on build configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70635.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70635
- https://www.vulncheck.com/advisories/timescaledb-out-of-bounds-read-dos-via-bulk-dictionary-decompression-negative-index
- https://github.com/timescale/timescaledb/pull/10360
- https://github.com/timescale/timescaledb/commit/517c13e7cc6afadb4a7deaa7a5a5a29065e5b5a3
- https://github.com/timescale/timescaledb
