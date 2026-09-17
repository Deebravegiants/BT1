# [C] CVE-2019-11365

## Summary
Severity: Critical
Advisory: CVE-2019-11365
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-20
Source: https://osv.dev/vulnerability/CVE-2019-11365
Type: osv

## Details
An issue was discovered in atftpd in atftp 0.7.1. A remote attacker may send a crafted packet triggering a stack-based buffer overflow due to an insecurely implemented strncpy call. The vulnerability is triggered by sending an error packet of 3 bytes or fewer. There are multiple instances of this vulnerable strncpy pattern within the code base, specifically within tftpd_file.c, tftp_file.c, tftpd_mtftp.c, and tftp_mtftp.c.

## References
- https://seclists.org/bugtraq/2019/May/16
- https://usn.ubuntu.com/4540-1/
- https://lists.debian.org/debian-lts-announce/2019/05/msg00012.html
- https://security.gentoo.org/glsa/202003-14
- https://www.debian.org/security/2019/dsa-4438
- https://sourceforge.net/p/atftp/code/ci/abed7d245d8e8bdfeab24f9f7f55a52c3140f96b/
- https://pulsesecurity.co.nz/advisories/atftpd-multiple-vulnerabilities
