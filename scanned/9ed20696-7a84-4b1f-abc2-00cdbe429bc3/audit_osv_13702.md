# [M] CVE-2018-21016

## Summary
Severity: Medium
Advisory: CVE-2018-21016
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-09-16
Source: https://osv.dev/vulnerability/CVE-2018-21016
Type: osv

## Details
audio_sample_entry_AddBox() at isomedia/box_code_base.c in GPAC 0.7.1 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2020/01/msg00017.html
- https://github.com/gpac/gpac/issues/1180
