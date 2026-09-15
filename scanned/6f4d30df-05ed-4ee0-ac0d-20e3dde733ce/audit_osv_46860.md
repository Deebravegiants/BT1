# [H] CVE-2015-7236

## Summary
Severity: High
Advisory: CVE-2015-7236
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2015-10-01
Source: https://osv.dev/vulnerability/CVE-2015-7236
Type: osv

## Details
Use-after-free vulnerability in xprt_set_caller in rpcb_svc_com.c in rpcbind 0.2.1 and earlier allows remote attackers to cause a denial of service (daemon crash) via crafted packets, involving a PMAP_CALLIT code.

## References
- http://www.debian.org/security/2015/dsa-3366
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.ubuntu.com/usn/USN-2756-1
- https://security.FreeBSD.org/advisories/FreeBSD-SA-15:24.rpcbind.asc
- https://security.gentoo.org/glsa/201611-17
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/171030.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/172152.html
- http://www.openwall.com/lists/oss-security/2015/09/17/1
- http://www.openwall.com/lists/oss-security/2015/09/17/6
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/76771
- http://www.securitytracker.com/id/1033673
- http://www.spinics.net/lists/linux-nfs/msg53045.html
