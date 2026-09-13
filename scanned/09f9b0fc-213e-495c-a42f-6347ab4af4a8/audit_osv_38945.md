# [H] xfrm6: fix uninitialized saddr in xfrm6_get_saddr()

## Summary
Severity: High
Advisory: CVE-2026-43139
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43139
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm6: fix uninitialized saddr in xfrm6_get_saddr()

xfrm6_get_saddr() does not check the return value of
ipv6_dev_get_saddr(). When ipv6_dev_get_saddr() fails to find a suitable
source address (returns -EADDRNOTAVAIL), saddr->in6 is left
uninitialized, but xfrm6_get_saddr() still returns 0 (success).

This causes the caller xfrm_tmpl_resolve_one() to use the uninitialized
address in xfrm_state_find(), triggering KMSAN warning:

=====================================================
BUG: KMSAN: uninit-value in xfrm_state_find+0x2424/0xa940
 xfrm_state_find+0x2424/0xa940
 xfrm_resolve_and_create_bundle+0x906/0x5a20
 xfrm_lookup_with_ifid+0xcc0/0x3770
 xfrm_lookup_route+0x63/0x2b0
 ip_route_output_flow+0x1ce/0x270
 udp_sendmsg+0x2ce1/0x3400
 inet_sendmsg+0x1ef/0x2a0
 __sock_sendmsg+0x278/0x3d0
 __sys_sendto+0x593/0x720
 __x64_sys_sendto+0x130/0x200
 x64_sys_call+0x332b/0x3e70
 do_syscall_64+0xd3/0xf80
 entry_SYSCALL_64_after_hwframe+0x77/0x7f

Local variable tmp.i.i created at:
 xfrm_resolve_and_create_bundle+0x3e3/0x5a20
 xfrm_lookup_with_ifid+0xcc0/0x3770
=====================================================

Fix by checking the return value of ipv6_dev_get_saddr() and propagating
the error.

## References
- https://git.kernel.org/stable/c/1799d8abeabc68ec05679292aaf6cba93b343c05
- https://git.kernel.org/stable/c/3dcd1664ac15eee6a690daec7c4ffc59190406f7
- https://git.kernel.org/stable/c/4f28141786e1fe884ce42a5197ba9beed540f0ea
- https://git.kernel.org/stable/c/6535867673bf301d52aa00593a4d1d18cc3922fa
- https://git.kernel.org/stable/c/719918fc88df6da023dfff370cd965151a5afd7f
- https://git.kernel.org/stable/c/c7221e7bd8fc2ef38a0b27be580d9d202281306b
- https://git.kernel.org/stable/c/dc0abce055134cb83b0d981d31ceb20dda419787
- https://git.kernel.org/stable/c/eb2ee15290af14c60b45cf2b73f5687d1d077d9b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43139.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43139
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
