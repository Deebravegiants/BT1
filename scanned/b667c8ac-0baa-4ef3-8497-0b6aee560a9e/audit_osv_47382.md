# [H] CVE-2016-4440

## Summary
Severity: High
Advisory: CVE-2016-4440
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-4440
Type: osv

## Details
arch/x86/kvm/vmx.c in the Linux kernel through 4.6.3 mishandles the APICv on/off state, which allows guest OS users to obtain direct APIC MSR access on the host OS, and consequently cause a denial of service (host OS crash) or possibly execute arbitrary code on the host OS, via x2APIC mode.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=3ce424e45411cf5a13105e0386b6ecf6eeb4f66f
- https://github.com/torvalds/linux/commit/3ce424e45411cf5a13105e0386b6ecf6eeb4f66f
- https://bugzilla.redhat.com/show_bug.cgi?id=1337806
- http://www.openwall.com/lists/oss-security/2016/05/20/2
