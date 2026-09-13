# [H] CVE-2018-7752

## Summary
Severity: High
Advisory: CVE-2018-7752
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-07
Source: https://osv.dev/vulnerability/CVE-2018-7752
Type: osv

## Details
GPAC through 0.7.1 has a Buffer Overflow in the gf_media_avc_read_sps function in media_tools/av_parsers.c, a different vulnerability than CVE-2018-1000100.

## References
- https://github.com/gpac/gpac/issues/997
- https://lists.debian.org/debian-lts-announce/2019/02/msg00040.html
- https://usn.ubuntu.com/3926-1/
- https://github.com/gpac/gpac/commit/90dc7f853d31b0a4e9441cba97feccf36d8b69a4
