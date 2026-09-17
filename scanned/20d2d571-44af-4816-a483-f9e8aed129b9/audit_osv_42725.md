# [H] TimescaleDB 2.29.1 Out-of-Bounds Read Information Disclosure via Dictionary Compression Reverse Iterator

## Summary
Severity: High
Advisory: CVE-2026-70634
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70634
Type: osv

## Details
TimescaleDB through 2.29.1, fixed in commit 517c13e, contains an out-of-bounds read in the Dictionary compression reverse row iterator (tsl/src/compression/algorithms/dictionary.c). The forward path validates the decoded index; the reverse path uses an assertion compiled out of release builds, leaving the 64-bit Simple8b index unvalidated and the read offset attacker-controlled. Attackers with DML access to a physical compressed relation can store a crafted datum and run a reverse-order scan. With a pass-by-value column type the out-of-bounds Datum is returned to the client as a normal column value, disclosing backend memory including the shared buffer pool, which SQL access control does not cover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70634.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70634
- https://www.vulncheck.com/advisories/timescaledb-out-of-bounds-read-information-disclosure-via-dictionary-compression-reverse-iterator
- https://github.com/timescale/timescaledb/pull/10360
- https://github.com/timescale/timescaledb/commit/517c13e7cc6afadb4a7deaa7a5a5a29065e5b5a3
- https://github.com/timescale/timescaledb
