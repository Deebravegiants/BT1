# [M] CVE-2021-28429

## Summary
Severity: Medium
Advisory: CVE-2021-28429
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/CVE-2021-28429
Type: osv

## Details
Integer overflow vulnerability in av_timecode_make_string in libavutil/timecode.c in FFmpeg version 4.3.2, allows local attackers to cause a denial of service (DoS) via crafted .mov file.

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commitdiff/c94875471e3ba3dc396c6919ff3ec9b14539cd71
