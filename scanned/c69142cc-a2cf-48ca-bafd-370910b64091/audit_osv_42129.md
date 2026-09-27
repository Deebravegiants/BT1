# [H] KVM: nVMX: Hide shadow VMCS right after VMCLEAR

## Summary
Severity: High
Advisory: CVE-2026-64562
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-64562
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: nVMX: Hide shadow VMCS right after VMCLEAR

free_nested() frees the shadow VMCS while vmcs01 still points to it. But
because it is asynchronous with respect to loaded_vmcs_clear(), the vCPU
might migrate before the pointer is cleared and __loaded_vmcs_clear()
may then execute VMCLEAR.

The VMCS needs to stay attached until its explicit VMCLEAR completes, but
then it can be hidden and the page safely freed.

## References
- https://git.kernel.org/stable/c/1dabef6e206568bf9d9ade74f6e56a48ea35695d
- https://git.kernel.org/stable/c/4f50e6aec16f69627dbad5704d1e90a255d766a7
- https://git.kernel.org/stable/c/589419470030a89f16cf19300658b6dc644ca946
- https://git.kernel.org/stable/c/622ebfac01ba4f9c0060cebd41257fe46fc4a0b3
- https://git.kernel.org/stable/c/8001d2ce9d9bd09118ce523aef595aa094573ae3
- https://git.kernel.org/stable/c/af56298e9d86e6098cd1d2e155cb2949b7c45412
- https://git.kernel.org/stable/c/b82c3144d8264265448292ca406f60bafeba3b6f
- https://git.kernel.org/stable/c/dc3eecfa219ebc9d01eaf7d1abd1441efe884dab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64562.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64562
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
