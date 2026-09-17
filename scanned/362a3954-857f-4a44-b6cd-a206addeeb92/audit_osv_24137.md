# [C] 9p: set req refcount to zero to avoid uninitialized usage

## Summary
Severity: Critical
Advisory: CVE-2022-50335
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2022-50335
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p: set req refcount to zero to avoid uninitialized usage

When a new request is allocated, the refcount will be zero if it is
reused, but if the request is newly allocated from slab, it is not fully
initialized before being added to idr.

If the p9_read_work got a response before the refcount initiated. It will
use a uninitialized req, which will result in a bad request data struct.

Here is the logs from syzbot.

Corrupted memory at 0xffff88807eade00b [ 0xff 0x07 0x00 0x00 0x00 0x00
0x00 0x00 . . . . . . . . ] (in kfence-#110):
 p9_fcall_fini net/9p/client.c:248 [inline]
 p9_req_put net/9p/client.c:396 [inline]
 p9_req_put+0x208/0x250 net/9p/client.c:390
 p9_client_walk+0x247/0x540 net/9p/client.c:1165
 clone_fid fs/9p/fid.h:21 [inline]
 v9fs_fid_xattr_set+0xe4/0x2b0 fs/9p/xattr.c:118
 v9fs_xattr_set fs/9p/xattr.c:100 [inline]
 v9fs_xattr_handler_set+0x6f/0x120 fs/9p/xattr.c:159
 __vfs_setxattr+0x119/0x180 fs/xattr.c:182
 __vfs_setxattr_noperm+0x129/0x5f0 fs/xattr.c:216
 __vfs_setxattr_locked+0x1d3/0x260 fs/xattr.c:277
 vfs_setxattr+0x143/0x340 fs/xattr.c:309
 setxattr+0x146/0x160 fs/xattr.c:617
 path_setxattr+0x197/0x1c0 fs/xattr.c:636
 __do_sys_setxattr fs/xattr.c:652 [inline]
 __se_sys_setxattr fs/xattr.c:648 [inline]
 __ia32_sys_setxattr+0xc0/0x160 fs/xattr.c:648
 do_syscall_32_irqs_on arch/x86/entry/common.c:112 [inline]
 __do_fast_syscall_32+0x65/0xf0 arch/x86/entry/common.c:178
 do_fast_syscall_32+0x33/0x70 arch/x86/entry/common.c:203
 entry_SYSENTER_compat_after_hwframe+0x70/0x82

Below is a similar scenario, the scenario in the syzbot log looks more
complicated than this one, but this patch can fix it.

     T21124                   p9_read_work
======================== second trans =================================
p9_client_walk
  p9_client_rpc
    p9_client_prepare_req
      p9_tag_alloc
        req = kmem_cache_alloc(p9_req_cache, GFP_NOFS);
        tag = idr_alloc
        << preempted >>
        req->tc.tag = tag;
                            /* req->[refcount/tag] == uninitialized */
                            m->rreq = p9_tag_lookup(m->client, m->rc.tag);
                              /* increments uninitalized refcount */

        refcount_set(&req->refcount, 2);
                            /* cb drops one ref */
                            p9_client_cb(req)
                            /* reader thread drops its ref:
                               request is incorrectly freed */
                            p9_req_put(req)
    /* use after free and ref underflow */
    p9_req_put(req)

To fix it, we can initialize the refcount to zero before add to idr.

## References
- https://git.kernel.org/stable/c/1cabce56626a61f4f02452cba61ad4332a4b73f8
- https://git.kernel.org/stable/c/26273ade77f54716e30dfd40ac6e85ceb54ac0f9
- https://git.kernel.org/stable/c/73c47b3123b351de2d3714a72a336c0f72f203af
- https://git.kernel.org/stable/c/967fc34f297e40fd2e068cf6b0c3eb4916228539
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50335.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50335
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
