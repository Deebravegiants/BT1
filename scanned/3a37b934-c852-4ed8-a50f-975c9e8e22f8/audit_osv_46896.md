# [M] CVE-2015-7802

## Summary
Severity: Medium
Advisory: CVE-2015-7802
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-04-20
Source: https://osv.dev/vulnerability/CVE-2015-7802
Type: osv

## Details
gifread.c in gif2png, as used in OptiPNG before 0.7.6, allows remote attackers to cause a denial of service (uninitialized memory read) via a crafted GIF file.

## References
- http://optipng.sourceforge.net/history.txt
- http://www.ubuntu.com/usn/USN-2951-1
- https://sourceforge.net/p/optipng/bugs/53/
