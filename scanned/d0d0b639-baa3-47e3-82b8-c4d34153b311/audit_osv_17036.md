# [C] CVE-2020-11558

## Summary
Severity: Critical
Advisory: CVE-2020-11558
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-05
Source: https://osv.dev/vulnerability/CVE-2020-11558
Type: osv

## Details
An issue was discovered in libgpac.a in GPAC 0.8.0, as demonstrated by MP4Box. audio_sample_entry_Read in isomedia/box_code_base.c does not properly decide when to make gf_isom_box_del calls. This leads to various use-after-free outcomes involving mdia_Read, gf_isom_delete_movie, and gf_isom_parse_movie_boxes.

## References
- https://github.com/gpac/gpac/commit/6063b1a011c3f80cee25daade18154e15e4c058c
- https://github.com/gpac/gpac/issues/1440
