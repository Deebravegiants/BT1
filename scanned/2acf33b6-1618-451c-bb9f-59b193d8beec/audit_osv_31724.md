# [M] bpf: Fix bpf_sk_select_reuseport() memory leak

## Summary
Severity: Medium
Advisory: CVE-2025-21683
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21683
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.127, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix bpf_sk_select_reuseport() memory leak

As pointed out in the original comment, lookup in sockmap can return a TCP
ESTABLISHED socket. Such TCP socket may have had SO_ATTACH_REUSEPORT_EBPF
set before it was ESTABLISHED. In other words, a non-NULL sk_reuseport_cb
does not imply a non-refcounted socket.

Drop sk's reference in both error paths.

unreferenced object 0xffff888101911800 (size 2048):
  comm "test_progs", pid 44109, jiffies 4297131437
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    80 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace (crc 9336483b):
    __kmalloc_noprof+0x3bf/0x560
    __reuseport_alloc+0x1d/0x40
    reuseport_alloc+0xca/0x150
    reuseport_attach_prog+0x87/0x140
    sk_reuseport_attach_bpf+0xc8/0x100
    sk_setsockopt+0x1181/0x1990
    do_sock_setsockopt+0x12b/0x160
    __sys_setsockopt+0x7b/0xc0
    __x64_sys_setsockopt+0x1b/0x30
    do_syscall_64+0x93/0x180
    entry_SYSCALL_64_after_hwframe+0x76/0x7e

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/0ab52a8ca6e156a64c51b5e7456cac9a0ebfd9bf
- https://git.kernel.org/stable/c/b02e70be498b138e9c21701c2f33f4018ca7cd5e
- https://git.kernel.org/stable/c/b3af60928ab9129befa65e6df0310d27300942bf
- https://git.kernel.org/stable/c/bb36838dac7bb334a3f3d7eb29875593ec9473fc
- https://git.kernel.org/stable/c/cccd51dd22574216e64e5d205489e634f86999f3
- https://git.kernel.org/stable/c/d0a3b3d1176d39218b8edb2a2d03164942ab9ccd
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21683.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21683
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
