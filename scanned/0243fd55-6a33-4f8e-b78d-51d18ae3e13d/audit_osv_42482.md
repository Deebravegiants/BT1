# [H] drm/amdkfd: fix 32-bit overflow in CWSR total size calculation

## Summary
Severity: High
Advisory: CVE-2026-68257
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68257
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.101, >=6.13.0 <6.18.42, >=6.18.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: fix 32-bit overflow in CWSR total size calculation

total_cwsr_size was computed in 32-bit before being used as a BO/SVM
allocation size.
With large ctx_save_restore_area_size and debug_memory_size
multiplied by the XCC count, the product can wrap,
yielding an undersized CWSR save area that firmware later overruns.

Promote total_cwsr_size to u64 and use check_add_overflow()/
check_mul_overflow() in both kfd_queue_acquire_buffers() and
kfd_queue_release_buffers().

(cherry picked from commit 319f7e13423ae3f486b9aea82f9ad2d6af0ee608)

## References
- https://git.kernel.org/stable/c/2b0386d4293920e690c0e017708f999b93cc729b
- https://git.kernel.org/stable/c/865532d54eb57b660b1cb1b0e1755776ce21b849
- https://git.kernel.org/stable/c/abce3276c57e36c955627307469b9f009057a467
- https://git.kernel.org/stable/c/b88ffe6593607364a8c06a48c6f29e55437cdf8e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68257.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68257
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
