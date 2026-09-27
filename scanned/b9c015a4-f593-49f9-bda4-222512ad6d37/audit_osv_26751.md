# [H] bpf: Zeroing allocated object from slab in bpf memory allocator

## Summary
Severity: High
Advisory: CVE-2023-53790
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53790
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Zeroing allocated object from slab in bpf memory allocator

Currently the freed element in bpf memory allocator may be immediately
reused, for htab map the reuse will reinitialize special fields in map
value (e.g., bpf_spin_lock), but lookup procedure may still access
these special fields, and it may lead to hard-lockup as shown below:

 NMI backtrace for cpu 16
 CPU: 16 PID: 2574 Comm: htab.bin Tainted: G             L     6.1.0+ #1
 Hardware name: QEMU Standard PC (i440FX + PIIX, 1996),
 RIP: 0010:queued_spin_lock_slowpath+0x283/0x2c0
 ......
 Call Trace:
  <TASK>
  copy_map_value_locked+0xb7/0x170
  bpf_map_copy_value+0x113/0x3c0
  __sys_bpf+0x1c67/0x2780
  __x64_sys_bpf+0x1c/0x20
  do_syscall_64+0x30/0x60
  entry_SYSCALL_64_after_hwframe+0x46/0xb0
 ......
  </TASK>

For htab map, just like the preallocated case, these is no need to
initialize these special fields in map value again once these fields
have been initialized. For preallocated htab map, these fields are
initialized through __GFP_ZERO in bpf_map_area_alloc(), so do the
similar thing for non-preallocated htab in bpf memory allocator. And
there is no need to use __GFP_ZERO for per-cpu bpf memory allocator,
because __alloc_percpu_gfp() does it implicitly.

## References
- https://git.kernel.org/stable/c/5d447e04290e78bdc1a3a6c321320d384e09c2f1
- https://git.kernel.org/stable/c/678ea18d6240299fd77d7000c8b1d7e5f274c8af
- https://git.kernel.org/stable/c/997849c4b969034e225153f41026657def66d286
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53790.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53790
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
