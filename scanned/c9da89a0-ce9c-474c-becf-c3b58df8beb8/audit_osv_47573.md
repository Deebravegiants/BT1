# [M] CVE-2016-8630

## Summary
Severity: Medium
Advisory: CVE-2016-8630
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-8630
Type: osv

## Details
The x86_decode_insn function in arch/x86/kvm/emulate.c in the Linux kernel before 4.8.7, when KVM is enabled, allows local users to cause a denial of service (host OS crash) via a certain use of a ModR/M byte in an undefined instruction.

## References
- http://www.securityfocus.com/bid/94459
- http://rhn.redhat.com/errata/RHSA-2017-0387.html
- http://rhn.redhat.com/errata/RHSA-2017-0386.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.7
- http://www.openwall.com/lists/oss-security/2016/11/22/3
- https://bugzilla.redhat.com/show_bug.cgi?id=1393350
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=d9092f52d7e61dd1557f2db2400ddb430e85937e
- https://github.com/torvalds/linux/commit/d9092f52d7e61dd1557f2db2400ddb430e85937e
