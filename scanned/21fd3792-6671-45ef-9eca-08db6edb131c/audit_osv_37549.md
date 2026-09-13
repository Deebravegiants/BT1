# [M] FreeRDP has a `size_t` underflow in ADPCM decoder leads to heap-buffer-overflow write

## Summary
Severity: Medium
Advisory: CVE-2026-31883
Aliases: GHSA-85x9-4xxp-xhm5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-31883
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.24.0, a size_t underflow in the IMA-ADPCM and MS-ADPCM audio decoders leads to heap-buffer-overflow write via the RDPSND audio channel. In libfreerdp/codec/dsp.c, the IMA-ADPCM and MS-ADPCM decoders subtract block header sizes from a size_t variable without checking for underflow. When nBlockAlign (received from the server) is set such that size % block_size == 0 triggers the header parsing at a point where size is smaller than the header (4 or 8 bytes), the subtraction wraps size to ~SIZE_MAX. The while (size > 0) loop then continues for an astronomical number of iterations. This vulnerability is fixed in 3.24.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31883.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-85x9-4xxp-xhm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-31883
- https://github.com/FreeRDP/FreeRDP/commit/16df2300e1e3f5a51f68fb1626429e58b531b7c8
