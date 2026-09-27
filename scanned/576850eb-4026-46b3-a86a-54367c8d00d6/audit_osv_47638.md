# [M] CVE-2016-9756

## Summary
Severity: Medium
Advisory: CVE-2016-9756
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-9756
Type: osv

## Details
arch/x86/kvm/emulate.c in the Linux kernel before 4.8.12 does not properly initialize Code Segment (CS) in certain error cases, which allows local users to obtain sensitive information from kernel stack memory via a crafted application.

## References
- http://lists.opensuse.org/opensuse-security-announce/2017-01/msg00000.html
- http://www.securityfocus.com/bid/94615
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.12
- https://bugzilla.redhat.com/show_bug.cgi?id=1400468
- https://github.com/torvalds/linux/commit/2117d5398c81554fbf803f5fd1dc55eb78216c0c
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2117d5398c81554fbf803f5fd1dc55eb78216c0c
- http://www.openwall.com/lists/oss-security/2016/12/01/1
