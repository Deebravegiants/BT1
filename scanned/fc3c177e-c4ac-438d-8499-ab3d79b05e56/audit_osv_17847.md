# [M] CVE-2020-20902

## Summary
Severity: Medium
Advisory: CVE-2020-20902
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2020-20902
Type: osv

## Details
A CWE-125: Out-of-bounds read vulnerability exists in long_term_filter function in g729postfilter.c in FFmpeg 4.2.1 during computation of the denominator of pseudo-normalized correlation R'(0), that could result in disclosure of information.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commitdiff%3Bh=0c61661a2cbe1b8b284c80ada1c2fdddf4992cad
- https://trac.ffmpeg.org/ticket/8176
