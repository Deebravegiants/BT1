# [H] CVE-2018-8897

## Summary
Severity: High
Advisory: CVE-2018-8897
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-08
Source: https://osv.dev/vulnerability/CVE-2018-8897
Type: osv

## Details
A statement in the System Programming Guide of the Intel 64 and IA-32 Architectures Software Developer's Manual (SDM) was mishandled in the development of some or all operating-system kernels, resulting in unexpected behavior for #DB exceptions that are deferred by MOV SS or POP SS, as demonstrated by (for example) privilege escalation in Windows, macOS, some Xen configurations, or FreeBSD, or a Linux kernel crash. The MOV to SS and POP SS instructions inhibit interrupts (including NMIs), data breakpoints, and single step trap exceptions until the instruction boundary following the next instruction (SDM Vol. 3A; section 6.8.3). (The inhibited data breakpoints are those on memory accessed by the MOV to SS or POP to SS instruction itself.) Note that debug exceptions are not inhibited by the interrupt enable (EFLAGS.IF) system flag (SDM Vol. 3A; section 2.3). If the instruction following the MOV to SS or POP to SS instruction is an instruction like SYSCALL, SYSENTER, INT 3, etc. that transfers control to the operating system at CPL < 3, the debug exception is delivered after the transfer to CPL < 3 is complete. OS kernels may not expect this order of events and may therefore experience unexpected behavior when it occurs.

## References
- https://www.exploit-db.com/exploits/45024/
- https://www.kb.cert.org/vuls/id/631579
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://lists.debian.org/debian-lts-announce/2018/11/msg00013.html
- https://lists.debian.org/debian-lts-announce/2018/06/msg00000.html
- https://support.apple.com/HT208742
- http://openwall.com/lists/oss-security/2018/05/08/1
- http://www.securitytracker.com/id/1040849
- https://access.redhat.com/errata/RHSA-2018:1319
- https://access.redhat.com/errata/RHSA-2018:1345
- https://access.redhat.com/errata/RHSA-2018:1349
- https://access.redhat.com/errata/RHSA-2018:1352
- https://usn.ubuntu.com/3641-1/
- http://openwall.com/lists/oss-security/2018/05/08/4
- https://access.redhat.com/errata/RHSA-2018:1346
- https://lists.debian.org/debian-lts-announce/2018/05/msg00015.html
- https://usn.ubuntu.com/3641-2/
- https://www.freebsd.org/security/advisories/FreeBSD-SA-18:06.debugreg.asc
- https://access.redhat.com/errata/RHSA-2018:1348
- https://www.debian.org/security/2018/dsa-4196
