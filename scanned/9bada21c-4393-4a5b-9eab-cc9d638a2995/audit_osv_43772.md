# [C] vdpa/mlx5: Fix buffer length in create_direct_keys()

## Summary
Severity: Critical
Advisory: CVE-2026-74712
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74712
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vdpa/mlx5: Fix buffer length in create_direct_keys()

We have seen in our CI the following KASAN message:
BUG: KASAN: slab-out-of-bounds in cmd_exec+0x550/0xca0 [mlx5_core]
Read of size 272 at addr 0000000176795020 by task qemu-system-s39/82764
[...]
[<000011388ab3a7a0>] cmd_exec+0x550/0xca0 [mlx5_core]
[<000011388ab3b61c>] mlx5_cmd_exec_cb+0x25c/0x4f0 [mlx5_core]
[<000011388b21e82e>] mlx5_vdpa_exec_async_cmds+0x22e/0x5e0 [mlx5_vdpa]
[<000011388b21fd44>] create_direct_keys+0x954/0xef0 [mlx5_vdpa]
[...]
The buggy address is located 4128 bytes inside of
allocated 4384-byte region [0000000176794000, 0000000176795120)

So in essence we read 16 bytes beyond 4384-byte allocation.
create_direct_keys calculates the pointer and length for in and out
buffers.
The size calculation for in includes the entire structure
size (out + in + mtt[]) but the pointer passed to cmd_exec points only
to the 'in' field, skipping the 'out' field.

This causes mlx5_copy_to_msg() to read beyond the allocated buffer
by sizeof(out) bytes when copying command data.

Properly calculate the input size to match the pointer and allocation size.

## References
- https://git.kernel.org/stable/c/6c8a9f7bc00301e533a5366384f3070a8e7f8430
- https://git.kernel.org/stable/c/727e1f569855df83579edbd73dcb4a0723543a12
- https://git.kernel.org/stable/c/cde8931a25392670dd59a0acfcab87a830ab66c5
- https://git.kernel.org/stable/c/ec3bb289cf19d526224117d5d450a5fd9cbd5ab2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74712.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74712
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
