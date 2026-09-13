# [H] CVE-2018-1124

## Summary
Severity: High
Advisory: CVE-2018-1124
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-23
Source: https://osv.dev/vulnerability/CVE-2018-1124
Type: osv

## Details
procps-ng before version 3.3.15 is vulnerable to multiple integer overflows leading to a heap corruption in file2strvec function. This allows a privilege escalation for a local attacker who can create entries in procfs by starting processes, which could result in crashes or arbitrary code execution in proc utilities run by other users.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00058.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00059.html
- http://seclists.org/oss-sec/2018/q2/122
- http://www.securityfocus.com/bid/104214
- http://www.securitytracker.com/id/1041057
- https://access.redhat.com/errata/RHSA-2018:1700
- https://access.redhat.com/errata/RHSA-2018:1777
- https://access.redhat.com/errata/RHSA-2018:1820
- https://access.redhat.com/errata/RHSA-2018:2267
- https://access.redhat.com/errata/RHSA-2018:2268
- https://access.redhat.com/errata/RHSA-2019:1944
- https://access.redhat.com/errata/RHSA-2019:2401
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://kc.mcafee.com/corporate/index?page=content&id=SB10241
- https://lists.debian.org/debian-lts-announce/2018/05/msg00021.html
- https://security.gentoo.org/glsa/201805-14
- https://usn.ubuntu.com/3658-1/
- https://usn.ubuntu.com/3658-2/
- https://www.debian.org/security/2018/dsa-4208
- https://www.exploit-db.com/exploits/44806/
