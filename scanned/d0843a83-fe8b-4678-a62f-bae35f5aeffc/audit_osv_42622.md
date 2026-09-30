# [M] hashcat through 7.1.2 Heap Buffer Overflow in outfile_write() via Oversized Username

## Summary
Severity: Medium
Advisory: CVE-2026-68768
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-68768
Type: osv

## Details
hashcat contains a heap-based buffer overflow (out-of-bounds write) in the outfile_write() function in src/outfile.c. When assembling output into a fixed-size buffer (HCBUFSIZ_LARGE, ~16 MB), the function sequentially appends the username, separator, hash, and plaintext via memcpy without validating that the accumulated length stays within the buffer capacity. When run with --username --show against a crafted hash file containing an oversized username that nearly fills the buffer, the total assembled output exceeds the buffer, causing a heap buffer overflow that can corrupt memory and crash the process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68768.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68768
- https://www.vulncheck.com/advisories/hashcat-through-heap-buffer-overflow-in-outfile-write-via-oversized-username
- https://github.com/hashcat/hashcat/issues/4740
- https://github.com/hashcat/hashcat/commit/68f56a2d8712867a8520bf4dcf07f6145c23df89
- https://github.com/hashcat/hashcat
- https://github.com/hashcat/hashcat/blob/v7.1.2/src/outfile.c#L654-L668
