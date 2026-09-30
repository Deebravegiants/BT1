# [M] CVE-2021-47189

## Summary
Severity: Medium
Advisory: CVE-2021-47189
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47189
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: fix memory ordering between normal and ordered work functions

Ordered work functions aren't guaranteed to be handled by the same thread
which executed the normal work functions. The only way execution between
normal/ordered functions is synchronized is via the WORK_DONE_BIT,
unfortunately the used bitops don't guarantee any ordering whatsoever.

This manifested as seemingly inexplicable crashes on ARM64, where
async_chunk::inode is seen as non-null in async_cow_submit which causes
submit_compressed_extents to be called and crash occurs because
async_chunk::inode suddenly became NULL. The call trace was similar to:

    pc : submit_compressed_extents+0x38/0x3d0
    lr : async_cow_submit+0x50/0xd0
    sp : ffff800015d4bc20

    <registers omitted for brevity>

    Call trace:
     submit_compressed_extents+0x38/0x3d0
     async_cow_submit+0x50/0xd0
     run_ordered_work+0xc8/0x280
     btrfs_work_helper+0x98/0x250
     process_one_work+0x1f0/0x4ac
     worker_thread+0x188/0x504
     kthread+0x110/0x114
     ret_from_fork+0x10/0x18

Fix this by adding respective barrier calls which ensure that all
accesses preceding setting of WORK_DONE_BIT are strictly ordered before
setting the flag. At the same time add a read barrier after reading of
WORK_DONE_BIT in run_ordered_work which ensures all subsequent loads
would be strictly ordered after reading the bit. This in turn ensures
are all accesses before WORK_DONE_BIT are going to be strictly ordered
before any access that can occur in ordered_func.

## References
- https://git.kernel.org/stable/c/804a9d239ae9cbe88e861a7cd62319cc6ec7b136
- https://git.kernel.org/stable/c/bd660a20fea3ec60a49709ef5360f145ec0fe779
- https://git.kernel.org/stable/c/ed058d735a70f4b063323f1a7bb33cda0f987513
- https://git.kernel.org/stable/c/45da9c1767ac31857df572f0a909fbe88fd5a7e9
- https://git.kernel.org/stable/c/47e6f9f69153247109042010f3a77579e9dc61ff
- https://git.kernel.org/stable/c/637d652d351fd4f263ef302dc52f3971d314e500
- https://git.kernel.org/stable/c/670f6b3867c8f0f11e5097f353b164cecfec6179
- https://git.kernel.org/stable/c/6adbc07ebcaf8bead08b21687d49e0fc94400987
