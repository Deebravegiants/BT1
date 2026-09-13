# [H] CVE-2019-13618

## Summary
Severity: High
Advisory: CVE-2019-13618
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-16
Source: https://osv.dev/vulnerability/CVE-2019-13618
Type: osv

## Details
In GPAC before 0.8.0, isomedia/isom_read.c in libgpac.a has a heap-based buffer over-read, as demonstrated by a crash in gf_m2ts_sync in media_tools/mpegts.c.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00017.html
- https://github.com/gpac/gpac/compare/440d475...6b4ab40
- https://github.com/gpac/gpac/issues/1250
