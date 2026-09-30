# [M] net, neigh: Fix null-ptr-deref in neigh_table_clear()

## Summary
Severity: Medium
Advisory: CVE-2022-49904
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49904
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net, neigh: Fix null-ptr-deref in neigh_table_clear()

When IPv6 module gets initialized but hits an error in the middle,
kenel panic with:

KASAN: null-ptr-deref in range [0x0000000000000598-0x000000000000059f]
CPU: 1 PID: 361 Comm: insmod
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
RIP: 0010:__neigh_ifdown.isra.0+0x24b/0x370
RSP: 0018:ffff888012677908 EFLAGS: 00000202
...
Call Trace:
 <TASK>
 neigh_table_clear+0x94/0x2d0
 ndisc_cleanup+0x27/0x40 [ipv6]
 inet6_init+0x21c/0x2cb [ipv6]
 do_one_initcall+0xd3/0x4d0
 do_init_module+0x1ae/0x670
...
Kernel panic - not syncing: Fatal exception

When ipv6 initialization fails, it will try to cleanup and calls:

neigh_table_clear()
  neigh_ifdown(tbl, NULL)
    pneigh_queue_purge(&tbl->proxy_queue, dev_net(dev == NULL))
    # dev_net(NULL) triggers null-ptr-deref.

Fix it by passing NULL to pneigh_queue_purge() in neigh_ifdown() if dev
is NULL, to make kernel not panic immediately.

## References
- https://git.kernel.org/stable/c/0d38b4ca6679e72860ff8730e79bb99d0e9fa3b0
- https://git.kernel.org/stable/c/1c89642e7f2b7ecc9635610653f5c2f0276c0051
- https://git.kernel.org/stable/c/2b45d6d0c41cb9593868e476681efb1aae5078a1
- https://git.kernel.org/stable/c/a99a8ec4c62180c889482a2ff6465033e0743458
- https://git.kernel.org/stable/c/b49f6b2f21f543d4dc88fb7b1ec2adccb822f27c
- https://git.kernel.org/stable/c/b736592de2aa53aee2d48d6b129bc0c892007bbe
- https://git.kernel.org/stable/c/f8017317cb0b279b8ab98b0f3901a2e0ac880dad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49904.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49904
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
