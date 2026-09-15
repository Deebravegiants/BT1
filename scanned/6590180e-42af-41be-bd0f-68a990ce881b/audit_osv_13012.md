# [H] CVE-2018-16864

## Summary
Severity: High
Advisory: CVE-2018-16864
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/CVE-2018-16864
Type: osv

## Details
An allocation of memory without limits, that could result in the stack clashing with another memory region, was discovered in systemd-journald when a program with long command line arguments calls syslog. A local attacker may use this flaw to crash systemd-journald or escalate his privileges. Versions through v240 are vulnerable.

## References
- http://www.securityfocus.com/bid/106523
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:0049
- https://access.redhat.com/errata/RHSA-2019:0204
- https://access.redhat.com/errata/RHSA-2019:0271
- https://access.redhat.com/errata/RHSA-2019:0342
- https://access.redhat.com/errata/RHSA-2019:0361
- https://access.redhat.com/errata/RHSA-2019:2402
- https://lists.debian.org/debian-lts-announce/2019/01/msg00016.html
- https://security.gentoo.org/glsa/201903-07
- https://security.netapp.com/advisory/ntap-20190117-0001/
- https://usn.ubuntu.com/3855-1/
- https://www.debian.org/security/2019/dsa-4367
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16864
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- http://www.openwall.com/lists/oss-security/2021/07/20/2
- https://www.qualys.com/2019/01/09/system-down/system-down.txt
