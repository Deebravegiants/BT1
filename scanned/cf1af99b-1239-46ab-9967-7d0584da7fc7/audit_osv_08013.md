# [H] CVE-2016-10009

## Summary
Severity: High
Advisory: CVE-2016-10009
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2017-01-05
Source: https://osv.dev/vulnerability/CVE-2016-10009
Type: osv

## Details
Untrusted search path vulnerability in ssh-agent.c in ssh-agent in OpenSSH before 7.4 allows remote attackers to execute arbitrary local PKCS#11 modules by leveraging control over a forwarded agent-socket.

## References
- http://packetstormsecurity.com/files/140261/OpenSSH-Arbitrary-Library-Loading.html
- http://packetstormsecurity.com/files/173661/OpenSSH-Forwarded-SSH-Agent-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2023/Jul/31
- http://www.openwall.com/lists/oss-security/2023/07/19/9
- http://www.openwall.com/lists/oss-security/2023/07/20/1
- http://www.securityfocus.com/bid/94968
- http://www.securitytracker.com/id/1037490
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.647637
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1009
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://lists.debian.org/debian-lts-announce/2018/09/msg00010.html
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03818en_us
- https://usn.ubuntu.com/3538-1/
- https://www.exploit-db.com/exploits/40963/
- https://www.openssh.com/txt/release-7.4
- http://www.openwall.com/lists/oss-security/2016/12/19/2
- https://access.redhat.com/errata/RHSA-2017:2029
- https://security.FreeBSD.org/advisories/FreeBSD-SA-17:01.openssh.asc
- https://security.netapp.com/advisory/ntap-20171130-0002/
- https://github.com/openbsd/src/commit/9476ce1dd37d3c3218d5640b74c34c65e5f4efe5
