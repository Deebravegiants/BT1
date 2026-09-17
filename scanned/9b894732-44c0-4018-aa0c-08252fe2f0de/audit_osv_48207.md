# [H] CVE-2017-2583

## Summary
Severity: High
Advisory: CVE-2017-2583
CVSS: 8.4 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-02-06
Source: https://osv.dev/vulnerability/CVE-2017-2583
Type: osv

## Details
The load_segment_descriptor implementation in arch/x86/kvm/emulate.c in the Linux kernel before 4.9.5 improperly emulates a "MOV SS, NULL selector" instruction, which allows guest OS users to cause a denial of service (guest OS crash) or gain guest OS privileges via a crafted application.

## References
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/95673
- https://access.redhat.com/errata/RHSA-2017:1615
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.5
- http://www.openwall.com/lists/oss-security/2017/01/19/2
- https://access.redhat.com/errata/RHSA-2017:1616
- http://www.debian.org/security/2017/dsa-3791
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=33ab91103b3415e12457e3104f0e4517ce12d0f3
- https://bugzilla.redhat.com/show_bug.cgi?id=1414735
- https://github.com/torvalds/linux/commit/33ab91103b3415e12457e3104f0e4517ce12d0f3
