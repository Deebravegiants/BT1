# [H] CVE-2020-20450

## Summary
Severity: High
Advisory: CVE-2020-20450
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-25
Source: https://osv.dev/vulnerability/CVE-2020-20450
Type: osv

## Details
FFmpeg 4.2 is affected by null pointer dereference passed as argument to libavformat/aviobuf.c, which could cause a Denial of Service.

## References
- https://www.debian.org/security/2021/dsa-4998
- https://trac.ffmpeg.org/ticket/7993
