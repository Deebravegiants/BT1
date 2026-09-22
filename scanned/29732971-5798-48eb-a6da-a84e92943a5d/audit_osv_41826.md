# [H] KVM: arm64: Correctly cap ZCR_EL2 provided by a guest hypervisor

## Summary
Severity: High
Advisory: CVE-2026-63941
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63941
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Correctly cap ZCR_EL2 provided by a guest hypervisor

ZCR_EL2 can be updated by a VHE guest hypervisor either using ZCR_EL2
(which traps) or ZCR_EL1 (which does not trap). KVM handles both in
different way:

- on ZCR_EL2 trap, ZCR_EL2.LEN is immediately capped at the VM's own
  VL limit. This has the potential to break existing SW that relies
  on the full LEN field to be stateful.

- on ZCR_EL1 access, we do absolutely nothing.

On restoring the SVE context for an L2 guest, we directly restore the
guest hypervisor's view of ZCR_EL2 into the physical ZCR_EL2. If the
guest's view of the register was updated using the ZCR_EL2 accessor,
the value has already been sanitised (with the caveat mentioned above).

But if the guest used ZCR_EL1, the raw value is written into the HW,
and the L2 guest can now access VLs that it shouldn't.

Fix all the above by moving the VL capping to the restore points,
ensuring that:

- the HW is always programmed with a capped value, irrespective of
  the accessor being used,

- the ZCR_EL2.LEN field is always completely stateful, irrespective
  of the accessor being used.

Additionally, move ZCR_EL2 to be a sanitised register, ensuring that
only the LEN field is actually stateful. This requires some creative
construction of the RES0 mask, as the sysreg generation script does
not yet generate RAZ/WI fields.

[maz: rewrote commit message, tidy up access_zcr_el2()]

## References
- https://git.kernel.org/stable/c/742a9b5ccd8c46caf983ca90c94f855466968e34
- https://git.kernel.org/stable/c/83726330748981372bde86ed5411d7b306612991
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63941.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63941
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
