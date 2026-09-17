# [H] CVE-2017-15602

## Summary
Severity: High
Advisory: CVE-2017-15602
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-18
Source: https://osv.dev/vulnerability/CVE-2017-15602
Type: osv

## Details
In GNU Libextractor 1.4, there is an integer signedness error for the chunk size in the EXTRACTOR_nsfe_extract_method function in plugins/nsfe_extractor.c, leading to an infinite loop for a crafted size.

## References
- https://ftp.gnu.org/gnu/libextractor/libextractor-1.6.tar.gz
- https://lists.debian.org/debian-lts-announce/2017/12/msg00000.html
- http://lists.gnu.org/archive/html/bug-libextractor/2017-10/msg00005.html
