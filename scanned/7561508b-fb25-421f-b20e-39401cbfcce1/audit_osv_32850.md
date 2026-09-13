# [H] page_pool: Fix use-after-free in page_pool_recycle_in_ring

## Summary
Severity: High
Advisory: CVE-2025-38129
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38129
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.259, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

page_pool: Fix use-after-free in page_pool_recycle_in_ring

syzbot reported a uaf in page_pool_recycle_in_ring:

BUG: KASAN: slab-use-after-free in lock_release+0x151/0xa30 kernel/locking/lockdep.c:5862
Read of size 8 at addr ffff8880286045a0 by task syz.0.284/6943

CPU: 0 UID: 0 PID: 6943 Comm: syz.0.284 Not tainted 6.13.0-rc3-syzkaller-gdfa94ce54f41 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/13/2024
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94 [inline]
 dump_stack_lvl+0x241/0x360 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:378 [inline]
 print_report+0x169/0x550 mm/kasan/report.c:489
 kasan_report+0x143/0x180 mm/kasan/report.c:602
 lock_release+0x151/0xa30 kernel/locking/lockdep.c:5862
 __raw_spin_unlock_bh include/linux/spinlock_api_smp.h:165 [inline]
 _raw_spin_unlock_bh+0x1b/0x40 kernel/locking/spinlock.c:210
 spin_unlock_bh include/linux/spinlock.h:396 [inline]
 ptr_ring_produce_bh include/linux/ptr_ring.h:164 [inline]
 page_pool_recycle_in_ring net/core/page_pool.c:707 [inline]
 page_pool_put_unrefed_netmem+0x748/0xb00 net/core/page_pool.c:826
 page_pool_put_netmem include/net/page_pool/helpers.h:323 [inline]
 page_pool_put_full_netmem include/net/page_pool/helpers.h:353 [inline]
 napi_pp_put_page+0x149/0x2b0 net/core/skbuff.c:1036
 skb_pp_recycle net/core/skbuff.c:1047 [inline]
 skb_free_head net/core/skbuff.c:1094 [inline]
 skb_release_data+0x6c4/0x8a0 net/core/skbuff.c:1125
 skb_release_all net/core/skbuff.c:1190 [inline]
 __kfree_skb net/core/skbuff.c:1204 [inline]
 sk_skb_reason_drop+0x1c9/0x380 net/core/skbuff.c:1242
 kfree_skb_reason include/linux/skbuff.h:1263 [inline]
 __skb_queue_purge_reason include/linux/skbuff.h:3343 [inline]

root cause is:

page_pool_recycle_in_ring
  ptr_ring_produce
    spin_lock(&r->producer_lock);
    WRITE_ONCE(r->queue[r->producer++], ptr)
      //recycle last page to pool
				page_pool_release
				  page_pool_scrub
				    page_pool_empty_ring
				      ptr_ring_consume
				      page_pool_return_page  //release all page
				  __page_pool_destroy
				     free_percpu(pool->recycle_stats);
				     free(pool) //free

     spin_unlock(&r->producer_lock); //pool->ring uaf read
  recycle_stat_inc(pool, ring);

page_pool can be free while page pool recycle the last page in ring.
Add producer-lock barrier to page_pool_release to prevent the page
pool from being free before all pages have been recycled.

recycle_stat_inc() is empty when CONFIG_PAGE_POOL_STATS is not
enabled, which will trigger Wempty-body build warning. Add definition
for pool stat macro to fix warning.

## References
- https://git.kernel.org/stable/c/1a8c0b61d4cb55c5440583ec9e7f86a730369e32
- https://git.kernel.org/stable/c/271683bb2cf32e5126c592b5d5e6a756fa374fd9
- https://git.kernel.org/stable/c/4914c0a166540e534a0c1d43affd329d95fb56fd
- https://git.kernel.org/stable/c/4ab8c0f8905c9c4d05e7f437e65a9a365573ff02
- https://git.kernel.org/stable/c/c2c906142293931e33ef4be79ebc36c25c4e21dd
- https://git.kernel.org/stable/c/d69f28ef7cdafdcf37ee310f38b1399e7d05f9a8
- https://git.kernel.org/stable/c/e869a85acc2e60dc554579b910826a4919d8cd98
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38129.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38129
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
