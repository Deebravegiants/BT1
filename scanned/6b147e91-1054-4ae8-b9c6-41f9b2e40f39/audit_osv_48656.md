# [H] CVE-2018-1087

## Summary
Severity: High
Advisory: CVE-2018-1087
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-15
Source: https://osv.dev/vulnerability/CVE-2018-1087
Type: osv

## Details
kernel KVM before versions kernel 4.16, kernel 4.16-rc7, kernel 4.17-rc1, kernel 4.17-rc2 and kernel 4.17-rc3 is vulnerable to a flaw in the way the Linux kernel's KVM hypervisor handled exceptions delivered after a stack switch operation via Mov SS or Pop SS instructions. During the stack switch operation, the processor did not deliver interrupts and exceptions, rather they are delivered once the first instruction after the stack switch is executed. An unprivileged KVM guest user could use this flaw to crash the guest or, potentially, escalate their privileges in the guest.

## References
- http://www.securityfocus.com/bid/104127
- http://www.securitytracker.com/id/1040862
- https://access.redhat.com/errata/RHSA-2018:1318
- https://access.redhat.com/errata/RHSA-2018:1347
- https://access.redhat.com/errata/RHSA-2018:1348
- https://usn.ubuntu.com/3641-1/
- https://access.redhat.com/errata/RHSA-2018:1345
- https://access.redhat.com/errata/RHSA-2018:1355
- https://access.redhat.com/errata/RHSA-2018:1524
- https://access.redhat.com/security/vulnerabilities/pop_ss
- https://usn.ubuntu.com/3641-2/
- https://www.debian.org/security/2018/dsa-4196
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1087
- http://www.openwall.com/lists/oss-security/2018/05/08/5
