# [M] FreeRDP has a heap-buffer-overflow in ecam_encoder_compress_h264

## Summary
Severity: Medium
Advisory: CVE-2026-24677
Aliases: GHSA-xw37-j744-f8v7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-24677
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.22.0, ecam_encoder_compress_h264 trusts server-controlled dimensions and does not validate the source buffer size, leading to an out-of-bounds read in sws_scale. This vulnerability is fixed in 3.22.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24677.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-xw37-j744-f8v7
- https://nvd.nist.gov/vuln/detail/CVE-2026-24677
- https://github.com/FreeRDP/FreeRDP/commit/d2d4f449312ddafd4a4c6c8a4f856c7f0d44a3b5
