# [M] CVE-2021-30020

## Summary
Severity: Medium
Advisory: CVE-2021-30020
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-30020
Type: osv

## Details
In the function gf_hevc_read_pps_bs_internal function in media_tools/av_parsers.c in GPAC 1.0.1 there is a loop, which with crafted file, pps->num_tile_columns may be larger than sizeof(pps->column_width), which results in a heap overflow in the loop.

## References
- https://github.com/gpac/gpac/commit/51cdb67ff7c5f1242ac58c5aa603ceaf1793b788
- https://github.com/gpac/gpac/issues/1722
