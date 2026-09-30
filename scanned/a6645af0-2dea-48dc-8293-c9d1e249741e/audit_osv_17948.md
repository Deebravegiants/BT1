# [M] CVE-2020-22020

## Summary
Severity: Medium
Advisory: CVE-2020-22020
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2020-22020
Type: osv

## Details
Buffer Overflow vulnerability in FFmpeg 4.2 in the build_diff_map function in libavfilter/vf_fieldmatch.c, which could let a remote malicious user cause a Denial of Service.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commitdiff%3Bh=ce5274c1385d55892a692998923802023526b765
- https://lists.debian.org/debian-lts-announce/2021/08/msg00018.html
- https://www.debian.org/security/2021/dsa-4990
- https://trac.ffmpeg.org/ticket/8239
