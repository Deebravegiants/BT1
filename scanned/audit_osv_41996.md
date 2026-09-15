# [H] KVM: x86: Ensure vendor's exit handler runs before fastpath userspace exits

## Summary
Severity: High
Advisory: CVE-2026-64284
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64284
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: x86: Ensure vendor's exit handler runs before fastpath userspace exits

Move the handling of fastpath userspace exits into vendor code to ensure
KVM runs vendor specific operations that need to run before userspace gains
control of the vCPU.  E.g. for VMX (and soon to be for SVM as well), KVM
needs to flush the PML buffer prior to exiting to userspace, otherwise any
memory written by the final KVM_RUN might never be flagged as dirty.

Note, waiting to snapshot CR0 and CR3 until svm_handle_exit() is flawed in
general, as that risks consuming stale state in a fastpath handler.  That
will be addressed in a future change.

## References
- https://git.kernel.org/stable/c/0ffedf43910e44b76c2c1db4e9fbf12b268190c1
- https://git.kernel.org/stable/c/4ad73ef0e7966ecfe67de0060537b4cb14d9acd4
- https://git.kernel.org/stable/c/b3436d9b9b1affe1c3191ac9831308923f5f03c3
- https://git.kernel.org/stable/c/f2ca2b5326211bd38490f0497eb583721ce0bbc0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64284.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
