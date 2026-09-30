# [M] FreeRDP: Out-of-Bounds Read in Planar RLE Decoder (planar_decompress_plane_rle / planar_decompress_plane_rle_only)

## Summary
Severity: Medium
Advisory: CVE-2026-69159
Aliases: CVE-2026-67306, GHSA-qrxx-7g3c-j6w3
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-69159
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.29.0, planar_decompress_plane_rle and planar_decompress_plane_rle_only in libfreerdp/codec/planar.c verify that a control byte exists but do not verify that the source buffer contains the zero to fifteen raw bytes declared by that control byte. A malicious RDP server can send a truncated planar bitmap or surface update whose final control byte claims additional raw bytes, causing the decoder to read beyond pSrcData while processing a color plane. This can crash the client and may disclose adjacent memory. This issue is fixed in version 3.29.0.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.29.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69159.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-qrxx-7g3c-j6w3
- https://nvd.nist.gov/vuln/detail/CVE-2026-69159
- https://github.com/FreeRDP/FreeRDP/commit/75a1ec61d444179ea64a4ec0835214cb9c4f7c18
- https://github.com/FreeRDP/FreeRDP/pull/13016
