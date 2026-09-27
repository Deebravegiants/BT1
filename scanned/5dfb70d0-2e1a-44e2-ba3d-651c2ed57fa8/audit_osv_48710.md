# [H] CVE-2018-12020

## Summary
Severity: High
Advisory: CVE-2018-12020
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-08
Source: https://osv.dev/vulnerability/CVE-2018-12020
Type: osv

## Details
mainproc.c in GnuPG before 2.2.8 mishandles the original filename during decryption and verification actions, which allows remote attackers to spoof the output that GnuPG sends on file descriptor 2 to other programs that use the "--status-fd 2" option. For example, the OpenPGP data might represent an original filename that contains line feed characters in conjunction with GOODSIG or VALIDSIG status codes.

## References
- http://www.securitytracker.com/id/1041051
- http://www.securityfocus.com/bid/104450
- http://openwall.com/lists/oss-security/2018/06/08/2
- http://packetstormsecurity.com/files/152703/Johnny-You-Are-Fired.html
- https://access.redhat.com/errata/RHSA-2018:2181
- https://github.com/RUB-NDS/Johnny-You-Are-Fired
- https://github.com/RUB-NDS/Johnny-You-Are-Fired/blob/master/paper/johnny-fired.pdf
- https://lists.gnupg.org/pipermail/gnupg-announce/2018q2/000425.html
- http://seclists.org/fulldisclosure/2019/Apr/38
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://lists.debian.org/debian-lts-announce/2021/12/msg00027.html
- https://usn.ubuntu.com/3675-2/
- https://www.debian.org/security/2018/dsa-4222
- https://www.debian.org/security/2018/dsa-4223
- https://www.debian.org/security/2018/dsa-4224
- https://access.redhat.com/errata/RHSA-2018:2180
- http://www.openwall.com/lists/oss-security/2019/04/30/4
- https://usn.ubuntu.com/3675-1/
- https://usn.ubuntu.com/3675-3/
- https://usn.ubuntu.com/3964-1/
