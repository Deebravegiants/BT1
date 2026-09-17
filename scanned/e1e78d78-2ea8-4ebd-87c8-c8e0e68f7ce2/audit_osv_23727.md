# [H] misc: fastrpc: fix list iterator in fastrpc_req_mem_unmap_impl

## Summary
Severity: High
Advisory: CVE-2022-49393
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49393
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: fix list iterator in fastrpc_req_mem_unmap_impl

This is another instance of incorrect use of list iterator and
checking it for NULL.

The list iterator value 'map' will *always* be set and non-NULL
by list_for_each_entry(), so it is incorrect to assume that the
iterator value will be NULL if the list is empty (in this case, the
check 'if (!map) {' will always be false and never exit as expected).

To fix the bug, use a new variable 'iter' as the list iterator,
while use the original variable 'map' as a dedicated pointer to
point to the found element.

Without this patch, Kernel crashes with below trace:

Unable to handle kernel access to user memory outside uaccess routines
 at virtual address 0000ffff7fb03750
...
Call trace:
 fastrpc_map_create+0x70/0x290 [fastrpc]
 fastrpc_req_mem_map+0xf0/0x2dc [fastrpc]
 fastrpc_device_ioctl+0x138/0xc60 [fastrpc]
 __arm64_sys_ioctl+0xa8/0xec
 invoke_syscall+0x48/0x114
 el0_svc_common.constprop.0+0xd4/0xfc
 do_el0_svc+0x28/0x90
 el0_svc+0x3c/0x130
 el0t_64_sync_handler+0xa4/0x130
 el0t_64_sync+0x18c/0x190
Code: 14000016 f94000a5 eb05029f 54000260 (b94018a6)
---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/2d12905aad462383f4e7a5fdb024d2b7ae2d10cf
- https://git.kernel.org/stable/c/c5c07c5958cf0c9af6e76813e6de15d42ee49822
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49393.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
