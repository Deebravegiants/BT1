# [H] KVM: arm64: Take the SRCU lock for page table walks in fault injection and AT emulation

## Summary
Severity: High
Advisory: CVE-2026-53277
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53277
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Take the SRCU lock for page table walks in fault injection and AT emulation

walk_s1() and kvm_walk_nested_s2() expect to be called while holding
kvm->srcu to guard against memslot changes. While this is generally
the case, __kvm_at_s12() and __kvm_find_s1_desc_level() call into the
respective walkers without taking kvm->srcu.

Fix by acquiring kvm->srcu prior to the table walk in both instances.

## References
- https://git.kernel.org/stable/c/97706097f9b851cfe55c3b00b083dfc2bcf542bc
- https://git.kernel.org/stable/c/ec42b4ed1b072ea2d03f086061aa67bad6d8de39
- https://git.kernel.org/stable/c/f2ca45b50d4216c9cc7ffabf50d9ad1932209251
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-53277.json
- https://access.redhat.com/errata/RHSA-2026:64775
- https://access.redhat.com/security/cve/CVE-2026-53277
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53277.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53277
- https://bugzilla.redhat.com/show_bug.cgi?id=2492725
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
