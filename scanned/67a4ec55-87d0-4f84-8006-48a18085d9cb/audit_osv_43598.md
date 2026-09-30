# [H] drm/amdkfd: fix uint32_t overflow in EOP ring buffer size alignment

## Summary
Severity: High
Advisory: CVE-2026-74447
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74447
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: fix uint32_t overflow in EOP ring buffer size alignment

eop_ring_buffer_size in struct queue_properties is a u32. In
kfd_queue_acquire_buffers() the expected EOP buffer size is computed as
ALIGN(eop_ring_buffer_size, PAGE_SIZE); ALIGN uses typeof(x), so the
addition is done in 32-bit. A user-supplied size of 0xFFFFF001 wraps to
0, causing kfd_queue_buffer_get() to skip its exact-size check (gated on
size != 0) and accept any BO mapped at the address. On GFX8/GFX9 the MQD
cp_hqd_eop_control is then programmed for an 8KB EOP ring backed by a 4KB
BO, so CP EOP writes can land past the buffer and fault the GPU.

Cast the operand to u64 so the alignment is computed in 64-bit; the size
check in kfd_queue_buffer_get() then rejects the oversized request.

(cherry picked from commit ae443117b742c357bfef3a7bddabf76fcf86e9ef)

## References
- https://git.kernel.org/stable/c/273548eb997c6be85230c1236b18784b09f6203c
- https://git.kernel.org/stable/c/6dc0b4b39ed4f11ef70f76ecea8537e35f45342b
- https://git.kernel.org/stable/c/7c54bd225d83bc1bcb44430ed4b4d3a5c36b1961
- https://git.kernel.org/stable/c/83463a96ea3c7d8ae636a4d6a0ba63c9ce410724
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74447.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
