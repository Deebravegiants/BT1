# [H] KVM: nVMX: Move vTPR vs. TPR Threshold consistency check into "normal" checks

## Summary
Severity: High
Advisory: CVE-2026-72287
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72287
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: nVMX: Move vTPR vs. TPR Threshold consistency check into "normal" checks

Move the off-by-default consistency check for vmcs12.tpr_threshold vs.
the virtual APIC vTPR into the "normal" controls checks, as waiting until
KVM has loaded some amount of state is unnecessary and actively dangerous.
Specifically, failure to unwind vmcs01.GUEST_CR3 to KVM's value when EPT
is disabled results in KVM running L1 with an L1-controlled CR3, not with
KVM's CR3!

Alternatively, KVM could simply reset the MMU to force a reload of
vmcs01.GUEST_CR3, but the _only_ reason the check was shoved into a "late"
flow was to wait until the vmcs12 pages were retrieved.  Rather than build
up more crusty code, simply access vTPR using a regular guest memory access
(performance isn't a concern).  To circumvent the restrictions that led to
KVM deferring nested_get_vmcs12_pages(), (a) use a VM-scoped API to read
guest memory so that it always hits non-SMM memslots (for RSM), and (b)
skip the check (since its off-by-default anyways) when the vCPU doesn't
want to run, i.e. when userspace is restoring/stuffing state.

If reading guest memory fails, simply skip the consistency check, as KVM's
de facto ABI is that VMX instruction accesses to non-existent memory get
PCI Bus Error semantics, where reads return 0xFFs.  And if vTPR=0xFF, then
the vTPR is guaranteed to be greater than or equal to TPR_THRESHOLD.

## References
- https://git.kernel.org/stable/c/7d066368f72e6192af7e21c5817626f6da666991
- https://git.kernel.org/stable/c/ebdac7554abb347ca4197be241116842161acd9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72287.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
