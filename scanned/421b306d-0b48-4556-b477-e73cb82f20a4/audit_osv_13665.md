# [H] CVE-2018-20760

## Summary
Severity: High
Advisory: CVE-2018-20760
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/CVE-2018-20760
Type: osv

## Details
In GPAC 0.7.1 and earlier, gf_text_get_utf8_line in media_tools/text_import.c in libgpac_static.a allows an out-of-bounds write because a certain -1 return value is mishandled.

## References
- https://lists.debian.org/debian-lts-announce/2019/02/msg00040.html
- https://usn.ubuntu.com/3926-1/
- https://github.com/gpac/gpac/commit/4c1360818fc8948e9307059fba4dc47ba8ad255d
- https://github.com/gpac/gpac/issues/1177
