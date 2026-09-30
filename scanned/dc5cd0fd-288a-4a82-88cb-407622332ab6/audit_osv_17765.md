# [M] CVE-2020-19481

## Summary
Severity: Medium
Advisory: CVE-2020-19481
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2020-19481
Type: osv

## Details
An issue was discovered in GPAC before 0.8.0, as demonstrated by MP4Box. It contains an invalid memory read in gf_m2ts_process_pmt in media_tools/mpegts.c that can cause a denial of service via a crafted MP4 file.

## References
- https://github.com/gpac/gpac/commit/2320eb73afba753b39b7147be91f7be7afc0eeb7
- https://github.com/gpac/gpac/issues/1265
- https://github.com/gpac/gpac/issues/1266
- https://github.com/gpac/gpac/issues/1267
