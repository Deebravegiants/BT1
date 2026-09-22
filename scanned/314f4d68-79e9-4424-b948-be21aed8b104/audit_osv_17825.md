# [M] CVE-2020-20445

## Summary
Severity: Medium
Advisory: CVE-2020-20445
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-25
Source: https://osv.dev/vulnerability/CVE-2020-20445
Type: osv

## Details
FFmpeg 4.2 is affected by a Divide By Zero issue via libavcodec/lpc.h, which allows a remote malicious user to cause a Denial of Service.

## References
- https://lists.debian.org/debian-lts-announce/2021/11/msg00012.html
- https://www.debian.org/security/2021/dsa-4990
- https://www.debian.org/security/2021/dsa-4998
- https://trac.ffmpeg.org/ticket/7996
