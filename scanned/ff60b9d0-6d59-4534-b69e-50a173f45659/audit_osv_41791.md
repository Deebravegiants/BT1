# [H] drm/amdkfd: fix a vulnerability of integer overflow in kfd debugger

## Summary
Severity: High
Advisory: CVE-2026-63881
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63881
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: fix a vulnerability of integer overflow in kfd debugger

get_queue_ids() computes array_size = num_queues * sizeof(uint32_t),
which could overflow on 32-bit size_t build. using array_size()
instead, it saturates to SIZE_MAX on overflow.

(cherry picked from commit 2d57a0475f085c08b49312dfd8edcb461845f285)

## References
- https://git.kernel.org/stable/c/4e5f808b454167cc58d7084a407a554d8ddc694d
- https://git.kernel.org/stable/c/4f9eeedc3d3151f8a226fd676c314a813edda5a1
- https://git.kernel.org/stable/c/5cf4a41aa0d74e4c83f82d2ce233b5189ed4b43c
- https://git.kernel.org/stable/c/93f5534b35a05ef8a0109c1eefa800062fee810a
- https://git.kernel.org/stable/c/de70a80992396ee306ee3a2810ad28aa1608ba9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63881.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63881
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
