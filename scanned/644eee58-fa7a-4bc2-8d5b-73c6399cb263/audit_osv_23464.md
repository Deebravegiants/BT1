# [H] misc: fastrpc: Fix use-after-free race condition for maps

## Summary
Severity: High
Advisory: CVE-2022-48872
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2022-48872
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.230, >=5.5.0 <5.10.165, >=5.11.0 <5.15.90, >=5.16.0 <6.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: Fix use-after-free race condition for maps

It is possible that in between calling fastrpc_map_get() until
map->fl->lock is taken in fastrpc_free_map(), another thread can call
fastrpc_map_lookup() and get a reference to a map that is about to be
deleted.

Rewrite fastrpc_map_get() to only increase the reference count of a map
if it's non-zero. Propagate this to callers so they can know if a map is
about to be deleted.

Fixes this warning:
refcount_t: addition on 0; use-after-free.
WARNING: CPU: 5 PID: 10100 at lib/refcount.c:25 refcount_warn_saturate
...
Call trace:
 refcount_warn_saturate
 [fastrpc_map_get inlined]
 [fastrpc_map_lookup inlined]
 fastrpc_map_create
 fastrpc_internal_invoke
 fastrpc_device_ioctl
 __arm64_sys_ioctl
 invoke_syscall

## References
- https://git.kernel.org/stable/c/079c78c68714f7d8d58e66c477b0243b31806907
- https://git.kernel.org/stable/c/556dfdb226ce1e5231d8836159b23f8bb0395bf4
- https://git.kernel.org/stable/c/61a0890cb95afec5c8a2f4a879de2b6220984ef1
- https://git.kernel.org/stable/c/96b328d119eca7563c1edcc4e1039a62e6370ecb
- https://git.kernel.org/stable/c/b171d0d2cf1b8387c72c8d325c5d5746fa271e39
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48872.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
