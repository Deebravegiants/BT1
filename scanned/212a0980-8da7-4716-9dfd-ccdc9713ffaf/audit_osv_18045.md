# [H] CVE-2020-23267

## Summary
Severity: High
Advisory: CVE-2020-23267
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2021-09-22
Source: https://osv.dev/vulnerability/CVE-2020-23267
Type: osv

## Details
An issue was discovered in gpac 0.8.0. The gf_hinter_track_process function in isom_hinter_track_process.c has a heap-based buffer overflow which can lead to a denial of service (DOS) via a crafted media file

## References
- https://github.com/gpac/gpac/issues/1479
