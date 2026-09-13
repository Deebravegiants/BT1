# [M] CVE-2020-27152

## Summary
Severity: Medium
Advisory: CVE-2020-27152
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-06
Source: https://osv.dev/vulnerability/CVE-2020-27152
Type: osv

## Details
An issue was discovered in ioapic_lazy_update_eoi in arch/x86/kvm/ioapic.c in the Linux kernel before 5.9.2. It has an infinite loop related to improper interaction between a resampler and edge triggering, aka CID-77377064c3a9.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.2
- https://bugzilla.kernel.org/show_bug.cgi?id=208767
- http://www.openwall.com/lists/oss-security/2020/11/03/1
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=77377064c3a94911339f13ce113b3abf265e06da
