# [M] CVE-2015-8845

## Summary
Severity: Medium
Advisory: CVE-2015-8845
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2015-8845
Type: osv

## Details
The tm_reclaim_thread function in arch/powerpc/kernel/process.c in the Linux kernel before 4.4.1 on powerpc platforms does not ensure that TM suspend mode exists before proceeding with a tm_reclaim call, which allows local users to cause a denial of service (TM Bad Thing exception and panic) via a crafted application.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=7f821fc9c77a9b01fe7b1d6e72717b33d8d64142
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- https://github.com/torvalds/linux/commit/7f821fc9c77a9b01fe7b1d6e72717b33d8d64142
- https://github.com/torvalds/linux/commit/7f821fc9c77a9b01fe7b1d6e72717b33d8d64142
- https://bugzilla.redhat.com/show_bug.cgi?id=1326540
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.1
- http://www.openwall.com/lists/oss-security/2016/04/13/1
- http://www.securitytracker.com/id/1035594
