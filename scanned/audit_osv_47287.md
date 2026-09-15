# [M] CVE-2016-2191

## Summary
Severity: Medium
Advisory: CVE-2016-2191
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-04-13
Source: https://osv.dev/vulnerability/CVE-2016-2191
Type: osv

## Details
The bmp_read_rows function in pngxtern/pngxrbmp.c in OptiPNG before 0.7.6 allows remote attackers to cause a denial of service (invalid memory write and crash) via a series of delta escapes in a crafted BMP image.

## References
- http://www.securityfocus.com/archive/1/537972/100/0/threaded
- http://www.openwall.com/lists/oss-security/2016/04/04/2
- https://security.gentoo.org/glsa/201608-01
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00061.html
- http://seclists.org/fulldisclosure/2016/Apr/15
- http://www.ubuntu.com/usn/USN-2951-1
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00065.html
- http://www.debian.org/security/2016/dsa-3546
- https://sourceforge.net/p/optipng/bugs/59/
- http://packetstormsecurity.com/files/136553/Optipng-Invalid-Write.html
