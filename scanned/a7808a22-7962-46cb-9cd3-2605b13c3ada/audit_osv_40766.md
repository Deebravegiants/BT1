# [H] FreeRDP: Out-of-bounds read in H.264 YUV-to-RGB conversion due to decoder/surface dimension mismatch

## Summary
Severity: High
Advisory: CVE-2026-55192
Aliases: GHSA-3mmf-qh4f-frm6
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-55192
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.27.0, FreeRDP H.264 decoder backends can return YUV planes sized from the bitstream without comparing the decoded width and height to the RDPGFX surface dimensions used to validate region rectangles. A malicious RDP server can provide an AVC420 or AVC444 bitstream whose decoded frame is smaller than the negotiated surface, causing yuv420_context_decode and the YUV-to-RGB conversion paths to read beyond the decoder-owned planes in libfreerdp/codec/h264.c and the selected H.264 backend. This can disclose client memory or crash the client. This issue is fixed in version 3.27.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.27.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55192.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-3mmf-qh4f-frm6
- https://nvd.nist.gov/vuln/detail/CVE-2026-55192
- https://github.com/FreeRDP/FreeRDP/commit/0cd45b70bb1fe6befd258ff64c46461947e99adb
- https://github.com/FreeRDP/FreeRDP/pull/12873
