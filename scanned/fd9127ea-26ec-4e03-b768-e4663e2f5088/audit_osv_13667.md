# [H] CVE-2018-20762

## Summary
Severity: High
Advisory: CVE-2018-20762
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-06
Source: https://osv.dev/vulnerability/CVE-2018-20762
Type: osv

## Details
GPAC version 0.7.1 and earlier has a buffer overflow vulnerability in the cat_multiple_files function in applications/mp4box/fileimport.c when MP4Box is used for a local directory containing crafted filenames.

## References
- https://lists.debian.org/debian-lts-announce/2019/02/msg00040.html
- https://usn.ubuntu.com/3926-1/
- https://github.com/gpac/gpac/commit/35ab4475a7df9b2a4bcab235e379c0c3ec543658
- https://github.com/gpac/gpac/issues/1187
