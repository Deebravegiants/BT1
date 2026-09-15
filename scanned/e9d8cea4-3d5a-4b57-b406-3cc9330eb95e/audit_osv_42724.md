# [M] TimescaleDB 2.29.1 Out-of-Bounds Read DoS via Gorilla Compression Reverse Iterator

## Summary
Severity: Medium
Advisory: CVE-2026-70633
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70633
Type: osv

## Details
TimescaleDB through 2.29.1, fixed in commit 517c13e, contains an out-of-bounds read vulnerability in the Gorilla compression reverse row iterator that allows authenticated attackers to cause a denial of service by storing a crafted compressed datum with an internally inconsistent BitArray. Attackers with DML access to a compressed hypertable can trigger an unsigned integer wraparound in the reverse iterator bucket index computation, causing a read beyond the end of the bucket array, resulting in a SIGSEGV crash that can be repeatedly triggered on each subsequent reverse-order scan.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70633.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70633
- https://www.vulncheck.com/advisories/timescaledb-out-of-bounds-read-dos-via-gorilla-compression-reverse-iterator
- https://github.com/timescale/timescaledb/pull/10360
- https://github.com/timescale/timescaledb/commit/517c13e7cc6afadb4a7deaa7a5a5a29065e5b5a3
- https://github.com/timescale/timescaledb
