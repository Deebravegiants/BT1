# [H] nfc: pn533: Clear nfc_target before being used

## Summary
Severity: High
Advisory: CVE-2022-50656
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2022-50656
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.3.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfc: pn533: Clear nfc_target before being used

Fix a slab-out-of-bounds read that occurs in nla_put() called from
nfc_genl_send_target() when target->sensb_res_len, which is duplicated
from an nfc_target in pn533, is too large as the nfc_target is not
properly initialized and retains garbage values. Clear nfc_targets with
memset() before they are used.

Found by a modified version of syzkaller.

BUG: KASAN: slab-out-of-bounds in nla_put
Call Trace:
 memcpy
 nla_put
 nfc_genl_dump_targets
 genl_lock_dumpit
 netlink_dump
 __netlink_dump_start
 genl_family_rcv_msg_dumpit
 genl_rcv_msg
 netlink_rcv_skb
 genl_rcv
 netlink_unicast
 netlink_sendmsg
 sock_sendmsg
 ____sys_sendmsg
 ___sys_sendmsg
 __sys_sendmsg
 do_syscall_64

## References
- https://git.kernel.org/stable/c/61a7e15d55fae329a245535c3bac494e401005b8
- https://git.kernel.org/stable/c/755019e37815a66bb0a23893debbd3dd640ccbd3
- https://git.kernel.org/stable/c/8bddef54cbe9ede5ac7478f1e1e968fcfe7e6f03
- https://git.kernel.org/stable/c/9da4a0411f3455e3885831d0758bee3e3d565bbc
- https://git.kernel.org/stable/c/9f28157778ede0d4f183f7ab3b46995bb400abbe
- https://git.kernel.org/stable/c/aae9c24ebd901f482e6c88b6f9e0c80dc5b536d6
- https://git.kernel.org/stable/c/aea9e64dec2cc6cd742e07ecd4e6236fc76b389b
- https://git.kernel.org/stable/c/bef2f478513e7367ef3b05441f6afca981de29be
- https://git.kernel.org/stable/c/e491285b4d08884b622638be8e4961eb43b0af64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50656.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50656
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
