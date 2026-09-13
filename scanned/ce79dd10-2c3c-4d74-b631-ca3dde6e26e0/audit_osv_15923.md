# [M] CVE-2019-20630

## Summary
Severity: Medium
Advisory: CVE-2019-20630
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-03-24
Source: https://osv.dev/vulnerability/CVE-2019-20630
Type: osv

## Details
An issue was discovered in libgpac.a in GPAC before 0.8.0, as demonstrated by MP4Box. It contains a heap-based buffer over-read in BS_ReadByte (called from gf_bs_read_bit) in utils/bitstream.c that can cause a denial of service via a crafted MP4 file.

## References
- https://github.com/gpac/gpac/commit/1ab4860609f2e7a35634930571e7d0531297e090
- https://github.com/gpac/gpac/issues/1268
