# [M] CVE-2018-11214

## Summary
Severity: Medium
Advisory: CVE-2018-11214
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-05-16
Source: https://osv.dev/vulnerability/CVE-2018-11214
Type: osv

## Details
An issue was discovered in libjpeg 9a. The get_text_rgb_row function in rdppm.c allows remote attackers to cause a denial of service (Segmentation fault) via a crafted file.

## References
- https://lists.debian.org/debian-lts-announce/2019/01/msg00015.html
- https://usn.ubuntu.com/3706-1/
- https://usn.ubuntu.com/3706-2/
- https://access.redhat.com/errata/RHSA-2019:2052
- https://github.com/ChijinZ/security_advisories/tree/master/libjpeg-v9a
