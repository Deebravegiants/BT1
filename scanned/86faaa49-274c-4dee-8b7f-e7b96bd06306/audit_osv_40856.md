# [H] FreeRDP: Heap out-of-bounds write in RemoteFX (RFX) Cache Bitmap V3 decode

## Summary
Severity: High
Advisory: CVE-2026-55827
Aliases: GHSA-c495-h83v-3prp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55827
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.27.1, FreeRDP clients launched with the non-default /cache:codec:rfx option pass desktop stride and height to RemoteFX decoding for Cache Bitmap V3 data while allocating bitmap->data only for the smaller DstWidth and DstHeight in gdi_Bitmap_Decompress, allowing a malicious RDP server to trigger a heap out-of-bounds write with attacker-controlled offset and content. This issue is fixed in version 3.27.1.

## References
- https://github.com/FreeRDP/FreeRDP/releases/tag/3.27.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55827.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-c495-h83v-3prp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55827
- https://github.com/FreeRDP/FreeRDP/commit/e58adf922ea4c0d5495e59a1fe488d70092e0e3e
- https://github.com/FreeRDP/FreeRDP/pull/12899
