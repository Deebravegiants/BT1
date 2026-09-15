# [M] CVE-2018-10963

## Summary
Severity: Medium
Advisory: CVE-2018-10963
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-10
Source: https://osv.dev/vulnerability/CVE-2018-10963
Type: osv

## Details
The TIFFWriteDirectorySec() function in tif_dirwrite.c in LibTIFF through 4.0.9 allows remote attackers to cause a denial of service (assertion failure and application crash) via a crafted file, a different vulnerability than CVE-2017-13726.

## References
- https://access.redhat.com/errata/RHSA-2019:2053
- https://lists.debian.org/debian-lts-announce/2018/07/msg00002.html
- https://usn.ubuntu.com/3864-1/
- https://www.debian.org/security/2018/dsa-4349
- http://bugzilla.maptools.org/show_bug.cgi?id=2795
