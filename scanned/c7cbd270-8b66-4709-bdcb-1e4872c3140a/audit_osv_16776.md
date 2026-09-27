# [M] CVE-2019-9717

## Summary
Severity: Medium
Advisory: CVE-2019-9717
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-9717
Type: osv

## Details
In Libav 12.3, a denial of service in the subtitle decoder allows attackers to hog the CPU via a crafted video file in Matroska format, because srt_to_ass in libavcodec/srtdec.c has a complex format argument to sscanf.

## References
- https://lgtm.com/security/
- https://github.com/libav/libav/blob/df744e3cf66548c9167ea857104a29d2ea92819e/libavcodec/srtdec.c#L90
