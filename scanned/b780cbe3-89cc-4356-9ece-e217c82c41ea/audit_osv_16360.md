# [M] CVE-2019-6111

## Summary
Severity: Medium
Advisory: CVE-2019-6111
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/CVE-2019-6111
Type: osv

## Details
An issue was discovered in OpenSSH 7.9. Due to the scp implementation being derived from 1983 rcp, the server chooses which files/directories are sent to the client. However, the scp client only performs cursory validation of the object name returned (only directory traversal attacks are prevented). A malicious scp server (or Man-in-The-Middle attacker) can overwrite arbitrary files in the scp client target directory. If recursive operation (-r) is performed, the server can manipulate subdirectories as well (for example, to overwrite the .ssh/authorized_keys file).

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00058.html
- https://lists.apache.org/thread.html/c45d9bc90700354b58fb7455962873c44229841880dcb64842fa7d23%40%3Cdev.mina.apache.org%3E
- https://lists.apache.org/thread.html/c7301cab36a86825359e1b725fc40304d1df56dc6d107c1fe885148b%40%3Cdev.mina.apache.org%3E
- https://lists.apache.org/thread.html/d540139359de999b0f1c87d05b715be4d7d4bec771e1ae55153c5c7a%40%3Cdev.mina.apache.org%3E
- https://lists.apache.org/thread.html/e47597433b351d6e01a5d68d610b4ba195743def9730e49561e8cf3f%40%3Cdev.mina.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W3YVQ2BPTOVDCFDVNC2GGF5P5ISFG37G/
- http://www.openwall.com/lists/oss-security/2019/04/18/1
- http://www.openwall.com/lists/oss-security/2022/08/02/1
- http://www.securityfocus.com/bid/106741
- https://access.redhat.com/errata/RHSA-2019:3702
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://cvsweb.openbsd.org/src/usr.bin/ssh/scp.c
- https://lists.debian.org/debian-lts-announce/2019/03/msg00030.html
- https://security.gentoo.org/glsa/201903-16
- https://security.netapp.com/advisory/ntap-20190213-0001/
- https://sintonen.fi/advisories/scp-client-multiple-vulnerabilities.txt
- https://usn.ubuntu.com/3885-1/
- https://usn.ubuntu.com/3885-2/
- https://www.debian.org/security/2019/dsa-4387
- https://www.freebsd.org/security/advisories/FreeBSD-EN-19:10.scp.asc
