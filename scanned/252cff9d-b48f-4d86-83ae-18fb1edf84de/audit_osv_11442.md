# [C] CVE-2017-7859

## Summary
Severity: Critical
Advisory: CVE-2017-7859
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2017-7859
Type: osv

## Details
FFmpeg before 2017-03-05 has an out-of-bounds write caused by a heap-based buffer overflow related to the ff_h264_slice_context_init function in libavcodec/h264dec.c.

## References
- http://www.securityfocus.com/bid/97663
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=713
