# [C] KVM: arm64: nv: Inject SEA if guest VNCR isn't normal memory

## Summary
Severity: Critical
Advisory: CVE-2026-72277
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72277
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: nv: Inject SEA if guest VNCR isn't normal memory

When constructing an L1 VNCR mapping, KVM unconditionally uses cacheable
memory attributes, even if the underlying PFN isn't memory. This gets
particularly hairy if the endpoint doesn't support cacheable memory
attributes, potentially throwing an SError on writeback...

While KVM does permit cacheable memory attributes on certain PFNMAP
VMAs, kvm_translate_vncr() isn't currently grabbing the VMA. So do the
simpler thing for now and just reject everything that isn't memory.

## References
- https://git.kernel.org/stable/c/4bd7dbe0b2243e6aa735cae4d5e1ff988b30b2a6
- https://git.kernel.org/stable/c/bc00e0e376ee3572f5d26c174473abef1e35decc
- https://git.kernel.org/stable/c/d5436e18e4fc2886ac306304d884ea3b92e1edbf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72277.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72277
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
