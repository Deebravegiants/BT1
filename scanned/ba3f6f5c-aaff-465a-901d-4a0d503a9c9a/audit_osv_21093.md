# [M] CVE-2021-40563

## Summary
Severity: Medium
Advisory: CVE-2021-40563
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-40563
Type: osv

## Details
A Segmentation fault exists casued by null pointer dereference exists in Gpac through 1.0.1 via the naludmx_create_avc_decoder_config function in reframe_nalu.c when using mp4box, which causes a denial of service.

## References
- https://github.com/gpac/gpac/issues/1892
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/commit/5ce0c906ed8599d218036b18b78e8126a496f137
