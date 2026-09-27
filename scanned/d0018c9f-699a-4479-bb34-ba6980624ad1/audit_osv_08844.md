# [M] CVE-2016-6313

## Summary
Severity: Medium
Advisory: CVE-2016-6313
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-6313
Type: osv

## Details
The mixing functions in the random number generator in Libgcrypt before 1.5.6, 1.6.x before 1.6.6, and 1.7.x before 1.7.3 and GnuPG before 1.4.21 make it easier for attackers to obtain the values of 160 bits by leveraging knowledge of the previous 4640 bits.

## References
- http://www.securitytracker.com/id/1036635
- https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git%3Ba=blob_plain%3Bf=NEWS
- http://rhn.redhat.com/errata/RHSA-2016-2674.html
- http://www.debian.org/security/2016/dsa-3649
- http://www.debian.org/security/2016/dsa-3650
- http://www.securityfocus.com/bid/92527
- http://www.ubuntu.com/usn/USN-3064-1
- http://www.ubuntu.com/usn/USN-3065-1
- https://lists.gnupg.org/pipermail/gnupg-announce/2016q3/000395.html
- https://security.gentoo.org/glsa/201610-04
- https://security.gentoo.org/glsa/201612-01
