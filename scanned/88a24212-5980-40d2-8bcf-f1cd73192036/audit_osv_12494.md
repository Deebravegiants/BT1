# [H] CVE-2018-12539

## Summary
Severity: High
Advisory: CVE-2018-12539
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-14
Source: https://osv.dev/vulnerability/CVE-2018-12539
Type: osv

## Details
In Eclipse OpenJ9 version 0.8, users other than the process owner may be able to use Java Attach API to connect to an Eclipse OpenJ9 or IBM JVM on the same machine and use Attach API operations, which includes the ability to execute untrusted native code. Attach API is enabled by default on Windows, Linux and AIX JVMs and can be disabled using the command line option -Dcom.ibm.tools.attach.enable=no.

## References
- http://www.securityfocus.com/bid/105126
- http://www.securitytracker.com/id/1041765
- https://access.redhat.com/errata/RHSA-2018:2568
- https://access.redhat.com/errata/RHSA-2018:2569
- https://access.redhat.com/errata/RHSA-2018:2575
- https://access.redhat.com/errata/RHSA-2018:2576
- https://access.redhat.com/errata/RHSA-2018:2712
- https://access.redhat.com/errata/RHSA-2018:2713
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=534589
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
