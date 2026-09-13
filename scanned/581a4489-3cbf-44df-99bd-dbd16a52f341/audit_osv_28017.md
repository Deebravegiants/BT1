# [H] KVM: x86/mmu: Write-protect L2 SPTEs in TDP MMU when clearing dirty status

## Summary
Severity: High
Advisory: CVE-2024-26990
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26990
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86/mmu: Write-protect L2 SPTEs in TDP MMU when clearing dirty status

Check kvm_mmu_page_ad_need_write_protect() when deciding whether to
write-protect or clear D-bits on TDP MMU SPTEs, so that the TDP MMU
accounts for any role-specific reasons for disabling D-bit dirty logging.

Specifically, TDP MMU SPTEs must be write-protected when the TDP MMU is
being used to run an L2 (i.e. L1 has disabled EPT) and PML is enabled.
KVM always disables PML when running L2, even when L1 and L2 GPAs are in
the some domain, so failing to write-protect TDP MMU SPTEs will cause
writes made by L2 to not be reflected in the dirty log.

[sean: massage shortlog and changelog, tweak ternary op formatting]

## References
- https://git.kernel.org/stable/c/2673dfb591a359c75080dd5af3da484b89320d22
- https://git.kernel.org/stable/c/cdf811a937471af2d1facdf8ae80e5e68096f1ed
- https://git.kernel.org/stable/c/e20bff0f1b2de9cfe303dd35ff46470104a87404
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26990.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26990
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
