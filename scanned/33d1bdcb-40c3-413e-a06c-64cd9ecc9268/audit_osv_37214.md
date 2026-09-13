# [M] FreeRDP has a heap-buffer-overflow in avc420_yuv_to_rgb via OOB regionRects

## Summary
Severity: Medium
Advisory: CVE-2026-29774
Aliases: GHSA-5q35-hv9x-7794
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-29774
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.24.0, a client-side heap buffer overflow occurs in the FreeRDP client's AVC420/AVC444 YUV-to-RGB conversion path due to missing horizontal bounds validation of H.264 metablock regionRects coordinates.  In yuv.c, the clamp() function (line 347) only validates top/bottom against the surface/YUV height, but never checks left/right against the surface width. When avc420_yuv_to_rgb (line 67) computes destination and source pointers using rect->left, it performs unchecked pointer arithmetic that can reach far beyond the allocated surface buffer. A malicious server sends a WIRE_TO_SURFACE_PDU_1 with AVC420 codec containing a regionRects entry where left greatly exceeds the surface width (e.g., left=60000 on a 128px surface). The H.264 bitstream decodes successfully, then yuv420_process_work_callback calls avc420_yuv_to_rgb which computes pDstPoint = pDstData + rect->top * nDstStep + rect->left * 4, writing 16-byte SSE vectors 1888+ bytes past the allocated heap region. This vulnerability is fixed in 3.24.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29774.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-5q35-hv9x-7794
- https://nvd.nist.gov/vuln/detail/CVE-2026-29774
- https://github.com/FreeRDP/FreeRDP/commit/6482b7a92fff3959582cef052d1967ad6bde3738
