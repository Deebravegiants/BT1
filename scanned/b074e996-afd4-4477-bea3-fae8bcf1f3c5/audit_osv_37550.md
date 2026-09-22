# [M] FreeRDP has a division-by-zero in ADPCM decoders when `nBlockAlign` is 0

## Summary
Severity: Medium
Advisory: CVE-2026-31884
Aliases: GHSA-jp7m-94ww-p56r
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-31884
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.24.0, division by zero in MS-ADPCM and IMA-ADPCM decoders when nBlockAlign is 0, leading to a crash. In libfreerdp/codec/dsp.c, both ADPCM decoders use size % block_size where block_size = context->common.format.nBlockAlign. The nBlockAlign value comes from the Server Audio Formats PDU on the RDPSND channel. The value 0 is not validated anywhere before reaching the decoder. When nBlockAlign = 0, the modulo operation causes a SIGFPE (floating point exception) crash. This vulnerability is fixed in 3.24.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31884.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-jp7m-94ww-p56r
- https://nvd.nist.gov/vuln/detail/CVE-2026-31884
- https://github.com/FreeRDP/FreeRDP/commit/03b48b3601d867afccac1cdc6081de7a275edce7
- https://github.com/FreeRDP/FreeRDP/commit/16df2300e1e3f5a51f68fb1626429e58b531b7c8
