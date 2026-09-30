# [H] CVE-2021-47624

## Summary
Severity: High
Advisory: CVE-2021-47624
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2021-47624
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sunrpc: fix reference count leaks in rpc_sysfs_xprt_state_change

The refcount leak issues take place in an error handling path. When the
3rd argument buf doesn't match with "offline", "online" or "remove", the
function simply returns -EINVAL and forgets to decrease the reference
count of a rpc_xprt object and a rpc_xprt_switch object increased by
rpc_sysfs_xprt_kobj_get_xprt() and
rpc_sysfs_xprt_kobj_get_xprt_switch(), causing reference count leaks of
both unused objects.

Fix this issue by jumping to the error handling path labelled with
out_put when buf matches none of "offline", "online" or "remove".

## References
- https://git.kernel.org/stable/c/4b22aa42bd4d2d630ef1854c139275c3532937cb
- https://git.kernel.org/stable/c/5f6024c05a2c0fdd180b29395aaf686d25af3a0f
- https://git.kernel.org/stable/c/776d794f28c95051bc70405a7b1fa40115658a18
