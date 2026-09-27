# [H] CVE-2019-9719

## Summary
Severity: High
Advisory: CVE-2019-9719
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-9719
Type: osv

## Details
A stack-based buffer overflow in the subtitle decoder in Libav 12.3 allows attackers to corrupt the stack via a crafted video file in Matroska format, because srt_to_ass in libavcodec/srtdec.c misuses snprintf. NOTE: Third parties dispute that this is a vulnerability because “no evidence of a vulnerability is provided” and only “a generic warning from a static code analysis” is provided

## References
- https://github.com/libav/libav/commits/master/libavcodec/srtdec.c
- https://lgtm.com/security/
- https://github.com/libav/libav/blob/df744e3cf66548c9167ea857104a29d2ea92819e/libavcodec/srtdec.c#L113
- https://lgtm.com/projects/g/libav/libav/snapshot/f5f553ca3bdca0c97dd08bbf002f0d8cb193788b/files/libavcodec/srtdec.c?sort=name&dir=ASC&mode=heatmap#xeec693aa6d85853b:1
