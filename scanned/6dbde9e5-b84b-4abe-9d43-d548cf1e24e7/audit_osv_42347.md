# [M] FreeRDP before 3.29.0 Heap Out-of-Bounds Read via TSMF

## Summary
Severity: Medium
Advisory: CVE-2026-67290
Aliases: GHSA-whq8-c3v3-p8v8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67290
Type: osv

## Details
FreeRDP before 3.29.0 contains a heap out-of-bounds read vulnerability in the TSMF FFmpeg decoder when parsing AVC1 MPEG2VIDEOINFO media types with insufficient ExtraData. Attackers can send malformed media format data from a server to trigger a crash by reading fixed offsets without validating source buffer length.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67290.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-whq8-c3v3-p8v8
- https://nvd.nist.gov/vuln/detail/CVE-2026-67290
- https://www.vulncheck.com/advisories/freerdp-before-heap-out-of-bounds-read-via-tsmf
- https://github.com/FreeRDP/FreeRDP/commit/8d3b86022f0d71aefa7bd2e466d2d391693a41b3
