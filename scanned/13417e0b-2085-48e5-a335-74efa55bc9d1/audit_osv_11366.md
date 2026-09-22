# [C] CVE-2017-7544

## Summary
Severity: Critical
Advisory: CVE-2017-7544
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-09-21
Source: https://osv.dev/vulnerability/CVE-2017-7544
Type: osv

## Details
libexif through 0.6.21 is vulnerable to out-of-bounds heap read vulnerability in exif_data_save_data_entry function in libexif/exif-data.c caused by improper length computation of the allocated data of an ExifMnote entry which can cause denial-of-service or possibly information disclosure.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2020/05/msg00016.html
- https://usn.ubuntu.com/4277-1/
- https://sourceforge.net/p/libexif/bugs/130/
