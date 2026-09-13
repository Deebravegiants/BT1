# [C] nfsd: clear acl_access/acl_default after releasing them

## Summary
Severity: Critical
Advisory: CVE-2025-21796
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21796
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.13 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

nfsd: clear acl_access/acl_default after releasing them

If getting acl_default fails, acl_access and acl_default will be released
simultaneously. However, acl_access will still retain a pointer pointing
to the released posix_acl, which will trigger a WARNING in
nfs3svc_release_getacl like this:

------------[ cut here ]------------
refcount_t: underflow; use-after-free.
WARNING: CPU: 26 PID: 3199 at lib/refcount.c:28
refcount_warn_saturate+0xb5/0x170
Modules linked in:
CPU: 26 UID: 0 PID: 3199 Comm: nfsd Not tainted
6.12.0-rc6-00079-g04ae226af01f-dirty #8
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS
1.16.1-2.fc37 04/01/2014
RIP: 0010:refcount_warn_saturate+0xb5/0x170
Code: cc cc 0f b6 1d b3 20 a5 03 80 fb 01 0f 87 65 48 d8 00 83 e3 01 75
e4 48 c7 c7 c0 3b 9b 85 c6 05 97 20 a5 03 01 e8 fb 3e 30 ff <0f> 0b eb
cd 0f b6 1d 8a3
RSP: 0018:ffffc90008637cd8 EFLAGS: 00010282
RAX: 0000000000000000 RBX: 0000000000000000 RCX: ffffffff83904fde
RDX: dffffc0000000000 RSI: 0000000000000008 RDI: ffff88871ed36380
RBP: ffff888158beeb40 R08: 0000000000000001 R09: fffff520010c6f56
R10: ffffc90008637ab7 R11: 0000000000000001 R12: 0000000000000001
R13: ffff888140e77400 R14: ffff888140e77408 R15: ffffffff858b42c0
FS:  0000000000000000(0000) GS:ffff88871ed00000(0000)
knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 0000562384d32158 CR3: 000000055cc6a000 CR4: 00000000000006f0
DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
Call Trace:
 <TASK>
 ? refcount_warn_saturate+0xb5/0x170
 ? __warn+0xa5/0x140
 ? refcount_warn_saturate+0xb5/0x170
 ? report_bug+0x1b1/0x1e0
 ? handle_bug+0x53/0xa0
 ? exc_invalid_op+0x17/0x40
 ? asm_exc_invalid_op+0x1a/0x20
 ? tick_nohz_tick_stopped+0x1e/0x40
 ? refcount_warn_saturate+0xb5/0x170
 ? refcount_warn_saturate+0xb5/0x170
 nfs3svc_release_getacl+0xc9/0xe0
 svc_process_common+0x5db/0xb60
 ? __pfx_svc_process_common+0x10/0x10
 ? __rcu_read_unlock+0x69/0xa0
 ? __pfx_nfsd_dispatch+0x10/0x10
 ? svc_xprt_received+0xa1/0x120
 ? xdr_init_decode+0x11d/0x190
 svc_process+0x2a7/0x330
 svc_handle_xprt+0x69d/0x940
 svc_recv+0x180/0x2d0
 nfsd+0x168/0x200
 ? __pfx_nfsd+0x10/0x10
 kthread+0x1a2/0x1e0
 ? kthread+0xf4/0x1e0
 ? __pfx_kthread+0x10/0x10
 ret_from_fork+0x34/0x60
 ? __pfx_kthread+0x10/0x10
 ret_from_fork_asm+0x1a/0x30
 </TASK>
Kernel panic - not syncing: kernel: panic_on_warn set ...

Clear acl_access/acl_default after posix_acl_release is called to prevent
UAF from being triggered.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/1fd94884174bd20beb1773990fd3b1aa877688d9
- https://git.kernel.org/stable/c/2e59b2b68782519560b3d6a41dd66a3d01a01cd3
- https://git.kernel.org/stable/c/55d947315fb5f67a35e4e1d3e01bb886b9c6decf
- https://git.kernel.org/stable/c/6f7cfee1a316891890c505563aa54f3476db52fd
- https://git.kernel.org/stable/c/7faf14a7b0366f153284db0ad3347c457ea70136
- https://git.kernel.org/stable/c/8a1737ae42c928384ab6447f6ee1a882510e85fa
- https://git.kernel.org/stable/c/f8d871523142f7895f250a856f8c4a4181614510
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21796.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21796
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
