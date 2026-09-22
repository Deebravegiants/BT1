# [M] CVE-2024-57184

## Summary
Severity: Medium
Advisory: CVE-2024-57184
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-01-24
Source: https://osv.dev/vulnerability/CVE-2024-57184
Type: osv

## Details
An issue was discovered in GPAC v0.8.0, as demonstrated by MP4Box. It contains a heap-based buffer overflow in gf_m2ts_process_pmt in media_tools/mpegts.c:2163 that can cause a denial of service (DOS) via a crafted MP4 file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57184.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57184
- https://github.com/gpac/gpac/issues/1421
- https://github.com/gpac/gpac/commit/8c5e847185d74462d674ee7d28fb46c29dae6dd2
