# [M] CVE-2019-9720

## Summary
Severity: Medium
Advisory: CVE-2019-9720
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-9720
Type: osv

## Details
A stack-based buffer overflow in the subtitle decoder in Libav 12.3 allows attackers to corrupt the stack via a crafted video file in Matroska format, because srt_to_ass in libavcodec/srtdec.c misuses snprintf.

## References
- https://lgtm.com/security/
- https://github.com/libav/libav/blob/df744e3cf66548c9167ea857104a29d2ea92819e/libavcodec/srtdec.c#L161
