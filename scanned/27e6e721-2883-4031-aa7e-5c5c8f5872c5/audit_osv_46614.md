# [M] CVE-2014-2532

## Summary
Severity: Medium
Advisory: CVE-2014-2532
CVSS: 4.9 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2014-03-18
Source: https://osv.dev/vulnerability/CVE-2014-2532
Type: osv

## Details
sshd in OpenSSH before 6.6 does not properly support wildcards on AcceptEnv lines in sshd_config, which allows remote attackers to bypass intended environment restrictions by using a substring located before a wildcard character.

## References
- http://advisories.mageia.org/MGASA-2014-0143.html
- http://aix.software.ibm.com/aix/efixes/security/openssh_advisory4.asc
- http://rhn.redhat.com/errata/RHSA-2014-1552.html
- http://secunia.com/advisories/57488
- http://secunia.com/advisories/57574
- http://secunia.com/advisories/59313
- http://secunia.com/advisories/59855
- http://www.debian.org/security/2014/dsa-2894
- http://www.mandriva.com/security/advisories?name=MDVSA-2014:068
- http://www.mandriva.com/security/advisories?name=MDVSA-2015:095
- http://www.oracle.com/technetwork/security-advisory/cpuapr2016v3-2985753.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://www.ubuntu.com/usn/USN-2155-1
- http://lists.apple.com/archives/security-announce/2015/Sep/msg00008.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-June/134026.html
- http://lists.fedoraproject.org/pipermail/package-announce/2014-May/133537.html
- http://marc.info/?l=bugtraq&m=141576985122836&w=2
- http://marc.info/?l=openbsd-security-announce&m=139492048027313&w=2
- http://www.securityfocus.com/bid/66355
