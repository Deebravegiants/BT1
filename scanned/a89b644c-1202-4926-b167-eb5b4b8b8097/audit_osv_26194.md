# [H] IB/hfi1: Fix bugs with non-PAGE_SIZE-end multi-iovec user SDMA requests

## Summary
Severity: High
Advisory: CVE-2023-52474
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2023-52474
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/hfi1: Fix bugs with non-PAGE_SIZE-end multi-iovec user SDMA requests

hfi1 user SDMA request processing has two bugs that can cause data
corruption for user SDMA requests that have multiple payload iovecs
where an iovec other than the tail iovec does not run up to the page
boundary for the buffer pointed to by that iovec.a

Here are the specific bugs:
1. user_sdma_txadd() does not use struct user_sdma_iovec->iov.iov_len.
   Rather, user_sdma_txadd() will add up to PAGE_SIZE bytes from iovec
   to the packet, even if some of those bytes are past
   iovec->iov.iov_len and are thus not intended to be in the packet.
2. user_sdma_txadd() and user_sdma_send_pkts() fail to advance to the
   next iovec in user_sdma_request->iovs when the current iovec
   is not PAGE_SIZE and does not contain enough data to complete the
   packet. The transmitted packet will contain the wrong data from the
   iovec pages.

This has not been an issue with SDMA packets from hfi1 Verbs or PSM2
because they only produce iovecs that end short of PAGE_SIZE as the tail
iovec of an SDMA request.

Fixing these bugs exposes other bugs with the SDMA pin cache
(struct mmu_rb_handler) that get in way of supporting user SDMA requests
with multiple payload iovecs whose buffers do not end at PAGE_SIZE. So
this commit fixes those issues as well.

Here are the mmu_rb_handler bugs that non-PAGE_SIZE-end multi-iovec
payload user SDMA requests can hit:
1. Overlapping memory ranges in mmu_rb_handler will result in duplicate
   pinnings.
2. When extending an existing mmu_rb_handler entry (struct mmu_rb_node),
   the mmu_rb code (1) removes the existing entry under a lock, (2)
   releases that lock, pins the new pages, (3) then reacquires the lock
   to insert the extended mmu_rb_node.

   If someone else comes in and inserts an overlapping entry between (2)
   and (3), insert in (3) will fail.

   The failure path code in this case unpins _all_ pages in either the
   original mmu_rb_node or the new mmu_rb_node that was inserted between
   (2) and (3).
3. In hfi1_mmu_rb_remove_unless_exact(), mmu_rb_node->refcount is
   incremented outside of mmu_rb_handler->lock. As a result, mmu_rb_node
   could be evicted by another thread that gets mmu_rb_handler->lock and
   checks mmu_rb_node->refcount before mmu_rb_node->refcount is
   incremented.
4. Related to #2 above, SDMA request submission failure path does not
   check mmu_rb_node->refcount before freeing mmu_rb_node object.

   If there are other SDMA requests in progress whose iovecs have
   pointers to the now-freed mmu_rb_node(s), those pointers to the
   now-freed mmu_rb nodes will be dereferenced when those SDMA requests
   complete.

## References
- https://git.kernel.org/stable/c/00cbce5cbf88459cd1aa1d60d0f1df15477df127
- https://git.kernel.org/stable/c/7e6010f79b58f45b204cf18aa58f4b73c3f30adc
- https://git.kernel.org/stable/c/9c4c6512d7330b743c4ffd18bd999a86ca26db0d
- https://git.kernel.org/stable/c/a2bd706ab63509793b5cd5065e685b7ef5cba678
- https://git.kernel.org/stable/c/c76cb8f4bdf26d04cfa5485a93ce297dba5e6a80
- https://git.kernel.org/stable/c/dce59b5443700fbd0d2433ec6e4d4cf063448844
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52474.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52474
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
