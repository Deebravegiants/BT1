# [M] CVE-2015-1350

## Summary
Severity: Medium
Advisory: CVE-2015-1350
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2015-1350
Type: osv

## Details
The VFS subsystem in the Linux kernel 3.x provides an incomplete set of requirements for setattr operations that underspecifies removing extended privilege attributes, which allows local users to cause a denial of service (capability stripping) via a failed invocation of a system call, as demonstrated by using chown to remove a capability from the ping or Wireshark dumpcap program.

## References
- http://marc.info/?l=linux-kernel&m=142153722930533&w=2
- http://www.openwall.com/lists/oss-security/2015/01/24/5
- http://www.securityfocus.com/bid/76075
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=770492
- https://bugzilla.redhat.com/show_bug.cgi?id=1185139
- http://marc.info/?l=linux-kernel&m=142153722930533&w=2
- http://www.openwall.com/lists/oss-security/2015/01/24/5
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=770492
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=770492
- http://marc.info/?l=linux-kernel&m=142153722930533&w=2
- https://bugzilla.redhat.com/show_bug.cgi?id=1185139
- https://bugzilla.redhat.com/show_bug.cgi?id=1185139
