# [H] rust_binder: use a u64 stride when cleaning up the offsets array

## Summary
Severity: High
Advisory: CVE-2026-64467
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64467
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

rust_binder: use a u64 stride when cleaning up the offsets array

Allocation's Drop walks the offsets array (binder_size_t = u64 entries),
cleaning up the objects, but it used usize instead of u64 for both the
stride and the per-entry read.

On 64-bit kernels (usize == u64) this is harmless, but on 32-bit kernels
it walks the 8-byte entries in 4-byte steps, iterating an N-entry array
2N times, and reads the always-zero high word as offset 0, cleaning up
the object at offset 0 N extra times. As a result the referenced node or
handle ends up with a lower reference count than it actually has (a
refcount over-decrement), and binder's reference accounting is corrupted;
for example, the owner can be notified of a strong reference release
(BR_RELEASE) even though references still remain.

Change the stride to u64, and read each entry as a u64, narrowing it to
usize with try_into().

On 32-bit ARM, when this over-decrement would drive a count below zero,
the driver's existing refcount guard refuses it and fires:

  rust_binder: Failure: refcount underflow!

## References
- https://git.kernel.org/stable/c/74920b1b4e474ba7a4de4323c0458deec49d210b
- https://git.kernel.org/stable/c/803c8a9502e9b97cd6ae937618ef4a8fd6274343
- https://git.kernel.org/stable/c/89b8cc948dce661af87527623b3a41cdd115e2f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64467.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64467
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
