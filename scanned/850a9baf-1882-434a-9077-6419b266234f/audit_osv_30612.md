# [H] riscv: kvm: Fix out-of-bounds array access

## Summary
Severity: High
Advisory: CVE-2024-53228
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53228
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: kvm: Fix out-of-bounds array access

In kvm_riscv_vcpu_sbi_init() the entry->ext_idx can contain an
out-of-bound index. This is used as a special marker for the base
extensions, that cannot be disabled. However, when traversing the
extensions, that special marker is not checked prior indexing the
array.

Add an out-of-bounds check to the function.

## References
- https://git.kernel.org/stable/c/332fa4a802b16ccb727199da685294f85f9880cb
- https://git.kernel.org/stable/c/3c49e1084a5df99807fc43dd318c491e6cbaa168
- https://git.kernel.org/stable/c/b1af648f0d610665c956ea4604d9f797e5c7e991
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53228.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53228
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
