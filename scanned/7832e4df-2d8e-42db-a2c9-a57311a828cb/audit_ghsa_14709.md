# [M] Undefined behaviour in `kvm_ioctls::ioctls::vm::VmFd::create_device`

## Summary
Severity: Medium
Advisory: GHSA-3qx8-rv27-j6gp
CWE: CWE-843
Ecosystem: crates.io
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-3qx8-rv27-j6gp
Type: github-advisory

## Affected
- crates.io: `kvm-ioctls` — affected >=0 <0.19.1

## Details
An issue was identified in the `VmFd::create_device function`, leading to undefined behavior and miscompilations on rustc 1.82.0 and newer due to the function's violation of Rust's pointer safety rules.

The function downcasted a mutable reference to its `struct kvm_create_device` argument to an immutable pointer, and then proceeded to pass this pointer to a mutating system call. Rustc 1.82.0 and newer elides subsequent reads of this structure's fields, meaning code will not see the value written by the kernel into the `fd` member. Instead, the code will observe the value that this field was initialized to prior to calling `VmFd::create_device` (usually, 0).

The issue started in kvm-ioctls 0.1.0 and was fixed in 0.19.1 by correctly using
a mutable pointer.

## References
- https://github.com/rust-vmm/kvm/pull/298
- https://github.com/rust-vmm/kvm-ioctls
- https://rustsec.org/advisories/RUSTSEC-2024-0428.html
