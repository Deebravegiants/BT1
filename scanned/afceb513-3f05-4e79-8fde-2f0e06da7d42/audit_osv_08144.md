# [H] CVE-2016-10708

## Summary
Severity: High
Advisory: CVE-2016-10708
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-21
Source: https://osv.dev/vulnerability/CVE-2016-10708
Type: osv

## Details
sshd in OpenSSH before 7.4 allows remote attackers to cause a denial of service (NULL pointer dereference and daemon crash) via an out-of-sequence NEWKEYS message, as demonstrated by Honggfuzz, related to kex.c and packet.c.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-676336.pdf
- https://kc.mcafee.com/corporate/index?page=content&id=SB10284
- https://support.f5.com/csp/article/K32485746?utm_source=f5support&amp%3Butm_medium=RSS
- http://www.securityfocus.com/bid/102780
- https://lists.debian.org/debian-lts-announce/2018/01/msg00031.html
- https://lists.debian.org/debian-lts-announce/2018/09/msg00010.html
- https://security.netapp.com/advisory/ntap-20180423-0003/
- https://usn.ubuntu.com/3809-1/
- https://www.openssh.com/releasenotes.html
- http://blog.swiecki.net/2018/01/fuzzing-tcp-servers.html
- https://anongit.mindrot.org/openssh.git/commit/?id=28652bca29046f62c7045e933e6b931de1d16737
