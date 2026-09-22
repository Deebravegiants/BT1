# [M] CVE-2021-30019

## Summary
Severity: Medium
Advisory: CVE-2021-30019
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-30019
Type: osv

## Details
In the adts_dmx_process function in filters/reframe_adts.c in GPAC 1.0.1, a crafted file may cause ctx->hdr.frame_size to be smaller than ctx->hdr.hdr_size, resulting in size to be a negative number and a heap overflow in the memcpy.

## References
- https://github.com/gpac/gpac/commit/22774aa9e62f586319c8f107f5bae950fed900bc
- https://github.com/gpac/gpac/issues/1723
