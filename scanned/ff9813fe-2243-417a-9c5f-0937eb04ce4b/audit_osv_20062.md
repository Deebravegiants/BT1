# [M] CVE-2021-30014

## Summary
Severity: Medium
Advisory: CVE-2021-30014
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-04-19
Source: https://osv.dev/vulnerability/CVE-2021-30014
Type: osv

## Details
There is a integer overflow in media_tools/av_parsers.c in the hevc_parse_slice_segment function in GPAC from v0.9.0-preview to 1.0.1 which results in a crash.

## References
- https://github.com/gpac/gpac/blob/v0.9.0-preview/src/media_tools/av_parsers.c#L6731
- https://github.com/gpac/gpac/commit/51cdb67ff7c5f1242ac58c5aa603ceaf1793b788
- https://github.com/gpac/gpac/issues/1721
