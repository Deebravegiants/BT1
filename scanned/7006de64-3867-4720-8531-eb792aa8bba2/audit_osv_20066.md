# [M] CVE-2021-30022

## Summary
Severity: Medium
Advisory: CVE-2021-30022
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-30022
Type: osv

## Details
There is a integer overflow in media_tools/av_parsers.c in the gf_avc_read_pps_bs_internal in GPAC from 0.5.2 to 1.0.1. pps_id may be a negative number, so it will not return. However, avc->pps only has 255 unit, so there is an overflow, which results a crash.

## References
- https://github.com/gpac/gpac/blob/v0.5.2/src/media_tools/av_parsers.c#L2344
- https://github.com/gpac/gpac/commit/51cdb67ff7c5f1242ac58c5aa603ceaf1793b788
- https://github.com/gpac/gpac/issues/1720
