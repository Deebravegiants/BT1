# [H] ptp: vmclock: prevent read-only mappings from becoming writable

## Summary
Severity: High
Advisory: CVE-2026-80724
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80724
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.47, >=6.19.0 <7.1.11, >=7.2.0 <7.2.1, >=7.3.0 <7.2.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ptp: vmclock: prevent read-only mappings from becoming writable

vmclock_miscdev_mmap() rejects writable mappings of the shared vmclock
ABI page with -EROFS, but leaves VM_MAYWRITE set.  Userspace can map the
page read-only and then upgrade it to writable with mprotect(), after
which the guest can corrupt the host-written timekeeping data (sequence
counter, UTC time, TSC offset) that the vmclock ABI defines as read-only.

Clear VM_MAYWRITE on the read-only path so the mapping cannot be
upgraded, as i915 does for its read-only objects and as fixed in drm/vc4
(CVE-2026-68445) and drm/panthor (CVE-2024-53071).

## References
- https://git.kernel.org/stable/c/0ce59c4148ecd1520c5592a63bb3c8991ee2d326
- https://git.kernel.org/stable/c/2496e141827102d6af512950057d402a2cfb2bfc
- https://git.kernel.org/stable/c/2e596e7814ba38cdc129991058b6c254ed37cb11
- https://git.kernel.org/stable/c/3f5677d2f817355147337f0453174c7bb0f3b66a
- https://git.kernel.org/stable/c/5b4f2bec7bea6c04084d720d731bedee7caf878d
- https://git.kernel.org/stable/c/a5edadbae57e2298a56cf7a4e774a027905a331f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80724.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80724
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
