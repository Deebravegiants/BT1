# [M] Zip Bomb in Lookyloo Capture Upload Allows Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-66913
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-66913
Type: osv

## Details
Lookyloo did not enforce limits on the decompressed size of uploaded capture archives and compressed HAR files.

An attacker could submit a specially crafted ZIP, gzip, or zlib-compressed capture containing data that expands to a very large size during processing. Because the application decompressed this content directly in memory without first limiting the output size, processing the malicious capture could exhaust available memory, terminate a web or worker process, or make the Lookyloo instance unavailable.

The vulnerability affects both full Lookyloo capture archive imports and API submissions containing gzip-compressed HAR data. Repeated exploitation could cause a persistent denial-of-service condition until the affected processes or instance are restarted.

The patch introduces:

  *  A 1 GB cumulative uncompressed-size limit for imported capture archives.
  *  Size-limited gzip and zlib decompression for compressed HAR files.
  *  Explicit detection and handling of suspected zip bombs.
  *  An HTTP 400 response when an oversized compressed HAR file is submitted through the API.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66913.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66913
- https://github.com/Lookyloo/lookyloo/commit/96589da290f018e356db7c0eaddf1aa501630ca7
- https://github.com/Lookyloo/lookyloo
