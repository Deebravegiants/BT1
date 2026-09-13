# [M] CVE-2025-69647

## Summary
Severity: Medium
Advisory: CVE-2025-69647
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2025-69647
Type: osv

## Details
GNU Binutils thru 2.45.1 readelf contains a denial-of-service vulnerability when processing a crafted binary with malformed DWARF loclists data. A logic flaw in the DWARF parsing code can cause readelf to repeatedly print the same table output without making forward progress, resulting in an unbounded output loop that never terminates unless externally interrupted. A local attacker can trigger this behavior by supplying a malicious input file, causing excessive CPU and I/O usage and preventing readelf from completing its analysis.

## References
- https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;h=455446bbdc8675f34808187de2bbad4682016ff7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69647.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69647
- https://sourceware.org/bugzilla/show_bug.cgi?id=33640
