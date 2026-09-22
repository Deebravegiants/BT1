# [C] RDMA/rtrs: Ensure 'ib_sge list' is accessible

## Summary
Severity: Critical
Advisory: CVE-2024-36476
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-15
Source: https://osv.dev/vulnerability/CVE-2024-36476
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.233, >=5.11.0 <5.15.176, >=5.16.0 <6.1.124, >=6.2.0 <6.6.70, >=6.7.0 <6.12.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rtrs: Ensure 'ib_sge list' is accessible

Move the declaration of the 'ib_sge list' variable outside the
'always_invalidate' block to ensure it remains accessible for use
throughout the function.

Previously, 'ib_sge list' was declared within the 'always_invalidate'
block, limiting its accessibility, then caused a
'BUG: kernel NULL pointer dereference'[1].
 ? __die_body.cold+0x19/0x27
 ? page_fault_oops+0x15a/0x2d0
 ? search_module_extables+0x19/0x60
 ? search_bpf_extables+0x5f/0x80
 ? exc_page_fault+0x7e/0x180
 ? asm_exc_page_fault+0x26/0x30
 ? memcpy_orig+0xd5/0x140
 rxe_mr_copy+0x1c3/0x200 [rdma_rxe]
 ? rxe_pool_get_index+0x4b/0x80 [rdma_rxe]
 copy_data+0xa5/0x230 [rdma_rxe]
 rxe_requester+0xd9b/0xf70 [rdma_rxe]
 ? finish_task_switch.isra.0+0x99/0x2e0
 rxe_sender+0x13/0x40 [rdma_rxe]
 do_task+0x68/0x1e0 [rdma_rxe]
 process_one_work+0x177/0x330
 worker_thread+0x252/0x390
 ? __pfx_worker_thread+0x10/0x10

This change ensures the variable is available for subsequent operations
that require it.

[1] https://lore.kernel.org/linux-rdma/6a1f3e8f-deb0-49f9-bc69-a9b03ecfcda7@fujitsu.com/

## References
- https://git.kernel.org/stable/c/143378075904e78b3b2a810099bcc3b3d82d762f
- https://git.kernel.org/stable/c/32e1e748a85bd52b20b3857d80fd166d22fa455a
- https://git.kernel.org/stable/c/6ffb5c1885195ae5211a12b4acd2d51843ca41b0
- https://git.kernel.org/stable/c/7eaa71f56a6f7ab87957213472dc6d4055862722
- https://git.kernel.org/stable/c/b238f61cc394d5fef27b26d7d9aa383ebfddabb0
- https://git.kernel.org/stable/c/fb514b31395946022f13a08e06a435f53cf9e8b3
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36476.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36476
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
