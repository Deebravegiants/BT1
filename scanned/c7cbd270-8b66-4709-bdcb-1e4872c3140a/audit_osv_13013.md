# [H] CVE-2018-16865

## Summary
Severity: High
Advisory: CVE-2018-16865
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/CVE-2018-16865
Type: osv

## Details
An allocation of memory without limits, that could result in the stack clashing with another memory region, was discovered in systemd-journald when many entries are sent to the journal socket. A local attacker, or a remote one if systemd-journal-remote is used, may use this flaw to crash systemd-journald or execute code with journald privileges. Versions through v240 are vulnerable.

## References
- http://packetstormsecurity.com/files/152841/System-Down-A-systemd-journald-Exploit.html
- http://seclists.org/fulldisclosure/2019/May/21
- http://www.openwall.com/lists/oss-security/2019/05/10/4
- http://www.openwall.com/lists/oss-security/2021/07/20/2
- http://www.securityfocus.com/bid/106525
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:0049
- https://access.redhat.com/errata/RHSA-2019:0204
- https://access.redhat.com/errata/RHSA-2019:0271
- https://access.redhat.com/errata/RHSA-2019:0342
- https://access.redhat.com/errata/RHSA-2019:0361
- https://access.redhat.com/errata/RHSA-2019:2402
- https://lists.debian.org/debian-lts-announce/2019/01/msg00016.html
- https://seclists.org/bugtraq/2019/May/25
- https://security.gentoo.org/glsa/201903-07
- https://security.netapp.com/advisory/ntap-20190117-0001/
- https://usn.ubuntu.com/3855-1/
- https://www.debian.org/security/2019/dsa-4367
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16865
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
