# [H] Bluetooth: Call iso_exit() on module unload

## Summary
Severity: High
Advisory: CVE-2024-50078
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50078
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: Call iso_exit() on module unload

If iso_init() has been called, iso_exit() must be called on module
unload. Without that, the struct proto that iso_init() registered with
proto_register() becomes invalid, which could cause unpredictable
problems later. In my case, with CONFIG_LIST_HARDENED and
CONFIG_BUG_ON_DATA_CORRUPTION enabled, loading the module again usually
triggers this BUG():

  list_add corruption. next->prev should be prev (ffffffffb5355fd0),
    but was 0000000000000068. (next=ffffffffc0a010d0).
  ------------[ cut here ]------------
  kernel BUG at lib/list_debug.c:29!
  Oops: invalid opcode: 0000 [#1] PREEMPT SMP PTI
  CPU: 1 PID: 4159 Comm: modprobe Not tainted 6.10.11-4+bt2-ao-desktop #1
  RIP: 0010:__list_add_valid_or_report+0x61/0xa0
  ...
    __list_add_valid_or_report+0x61/0xa0
    proto_register+0x299/0x320
    hci_sock_init+0x16/0xc0 [bluetooth]
    bt_init+0x68/0xd0 [bluetooth]
    __pfx_bt_init+0x10/0x10 [bluetooth]
    do_one_initcall+0x80/0x2f0
    do_init_module+0x8b/0x230
    __do_sys_init_module+0x15f/0x190
    do_syscall_64+0x68/0x110
  ...

## References
- https://git.kernel.org/stable/c/05f84d86169b2ebac185c5736a256823d42c425b
- https://git.kernel.org/stable/c/4af7ba39a1a02e16ee8cd0d3b6c6657f51b8ad7a
- https://git.kernel.org/stable/c/d458cd1221e9e56da3b2cc5518ad3225caa91f20
- https://git.kernel.org/stable/c/f905a7d95091e0d2605a3a1a157a9351f09ab2e1
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50078.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
