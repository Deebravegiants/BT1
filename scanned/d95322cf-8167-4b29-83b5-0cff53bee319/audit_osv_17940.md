# [M] CVE-2020-21896

## Summary
Severity: Medium
Advisory: CVE-2020-21896
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-22
Source: https://osv.dev/vulnerability/CVE-2020-21896
Type: osv

## Details
A Use After Free vulnerability in svg_dev_text_span_as_paths_defs function in source/fitz/svg-device.c in Artifex Software MuPDF 1.16.0 allows remote attackers to cause a denial of service via opening of a crafted PDF file.

## References
- http://www.ghostscript.com/cgi-bin/findgit.cgi?8719e07834d6a72b6b4131539e49ed1e8e2ff79e
- https://lists.debian.org/debian-lts-announce/2025/08/msg00017.html
- https://bugs.ghostscript.com/show_bug.cgi?id=701294
