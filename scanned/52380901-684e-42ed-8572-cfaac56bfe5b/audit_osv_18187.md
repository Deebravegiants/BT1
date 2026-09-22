# [M] CVE-2020-24829

## Summary
Severity: Medium
Advisory: CVE-2020-24829
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-08-04
Source: https://osv.dev/vulnerability/CVE-2020-24829
Type: osv

## Details
An issue was discovered in GPAC from v0.5.2 to v0.8.0, as demonstrated by MP4Box. It contains a heap-based buffer overflow in gf_m2ts_section_complete in media_tools/mpegts.c that can cause a denial of service (DOS) via a crafted MP4 file.

## References
- https://github.com/gpac/gpac/blob/v0.5.2/src/media_tools/mpegts.c#L2204
- https://github.com/gpac/gpac/issues/1422
- https://github.com/gpac/gpac/commit/8c5e847185d74462d674ee7d28fb46c29dae6dd2
