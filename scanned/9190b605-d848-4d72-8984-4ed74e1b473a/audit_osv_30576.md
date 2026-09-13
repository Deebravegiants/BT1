# [M] ipc: fix memleak if msg_init_ns failed in create_ipc_ns

## Summary
Severity: Medium
Advisory: CVE-2024-53175
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53175
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipc: fix memleak if msg_init_ns failed in create_ipc_ns

Percpu memory allocation may failed during create_ipc_ns however this
fail is not handled properly since ipc sysctls and mq sysctls is not
released properly. Fix this by release these two resource when failure.

Here is the kmemleak stack when percpu failed:

unreferenced object 0xffff88819de2a600 (size 512):
  comm "shmem_2nstest", pid 120711, jiffies 4300542254
  hex dump (first 32 bytes):
    60 aa 9d 84 ff ff ff ff fc 18 48 b2 84 88 ff ff  `.........H.....
    04 00 00 00 a4 01 00 00 20 e4 56 81 ff ff ff ff  ........ .V.....
  backtrace (crc be7cba35):
    [<ffffffff81b43f83>] __kmalloc_node_track_caller_noprof+0x333/0x420
    [<ffffffff81a52e56>] kmemdup_noprof+0x26/0x50
    [<ffffffff821b2f37>] setup_mq_sysctls+0x57/0x1d0
    [<ffffffff821b29cc>] copy_ipcs+0x29c/0x3b0
    [<ffffffff815d6a10>] create_new_namespaces+0x1d0/0x920
    [<ffffffff815d7449>] copy_namespaces+0x2e9/0x3e0
    [<ffffffff815458f3>] copy_process+0x29f3/0x7ff0
    [<ffffffff8154b080>] kernel_clone+0xc0/0x650
    [<ffffffff8154b6b1>] __do_sys_clone+0xa1/0xe0
    [<ffffffff843df8ff>] do_syscall_64+0xbf/0x1c0
    [<ffffffff846000b0>] entry_SYSCALL_64_after_hwframe+0x4b/0x53

## References
- https://git.kernel.org/stable/c/10209665b5bf199f8065b2e7d2b2dc6cdf227117
- https://git.kernel.org/stable/c/3d230cfd4b9b0558c7b2039ba1def2ce6b6cd158
- https://git.kernel.org/stable/c/8fed302872e26c7bf44d855c53a1cde747172d58
- https://git.kernel.org/stable/c/928de5fcd462498b8334107035da8ab85e316d8a
- https://git.kernel.org/stable/c/bc8f5921cd69188627c08041276238de222ab466
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53175.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53175
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
