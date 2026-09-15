# [M] CVE-2018-14048

## Summary
Severity: Medium
Advisory: CVE-2018-14048
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-13
Source: https://osv.dev/vulnerability/CVE-2018-14048
Type: osv

## Details
An issue has been found in libpng 1.6.34. It is a SEGV in the function png_free_data in png.c, related to the recommended error handling for png_read_image.

## References
- http://packetstormsecurity.com/files/152561/Slackware-Security-Advisory-libpng-Updates.html
- https://seclists.org/bugtraq/2019/Apr/30
- https://security.gentoo.org/glsa/201908-02
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- https://github.com/fouzhe/security/tree/master/libpng
- https://github.com/glennrp/libpng/issues/238
