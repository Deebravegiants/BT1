# [M] CVE-2018-10360

## Summary
Severity: Medium
Advisory: CVE-2018-10360
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-10360
Type: osv

## Details
The do_core_note function in readelf.c in libmagic.a in file 5.33 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted ELF file.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00053.html
- https://security.gentoo.org/glsa/201806-08
- https://usn.ubuntu.com/3686-1/
- https://usn.ubuntu.com/3686-2/
- https://github.com/file/file/commit/a642587a9c9e2dd7feacdf513c3643ce26ad3c22
