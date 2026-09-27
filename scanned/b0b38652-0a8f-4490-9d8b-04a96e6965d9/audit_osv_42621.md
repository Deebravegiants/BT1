# [M] hashcat through 7.1.2 Off-by-One Out-of-Bounds Heap Write in fgetl()

## Summary
Severity: Medium
Advisory: CVE-2026-68767
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-68767
Type: osv

## Details
hashcat's fgetl() function in src/filehandling.c writes a null terminator one byte past the caller's buffer when an input line is exactly the buffer length. Attackers can trigger this out-of-bounds heap write by providing a hash file, potfile, or wordlist containing a line of exactly HCBUFSIZ_LARGE bytes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68767.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68767
- https://www.vulncheck.com/advisories/hashcat-through-off-by-one-out-of-bounds-heap-write-in-fgetl
- https://github.com/hashcat/hashcat/issues/4739
- https://github.com/hashcat/hashcat/commit/93b55d37d3b2340013d4036f10181ddc67d44249
- https://github.com/hashcat/hashcat
- https://github.com/hashcat/hashcat/blob/v7.1.2/src/filehandling.c#L1032-L1060
