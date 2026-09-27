# [H] io-wq: check that the predecessor is hashed in io_wq_remove_pending()

## Summary
Severity: High
Advisory: CVE-2026-46274
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46274
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

io-wq: check that the predecessor is hashed in io_wq_remove_pending()

io_wq_remove_pending() needs to fix up wq->hash_tail[] if the cancelled
work was the tail of its hash bucket. When doing this, it checks whether
the preceding entry in acct->work_list has the same hash value, but
never checks that the predecessor is hashed at all. io_get_work_hash()
is simply atomic_read(&work->flags) >> IO_WQ_HASH_SHIFT, and the hash
bits are never set for non-hashed work, so it returns 0. Thus, when a
hashed bucket-0 work is cancelled while a non-hashed work is its list
predecessor, the check spuriously passes and a pointer to the non-hashed
io_kiocb is stored in wq->hash_tail[0].

Because non-hashed work is dequeued via the fast path in
io_get_next_work(), which never touches hash_tail[], the stale pointer
is never cleared. Therefore, after the non-hashed io_kiocb completes and
is freed back to req_cachep, wq->hash_tail[0] is a dangling pointer. The
io_wq is per-task (tctx->io_wq) and survives ring open/close, so the
dangling pointer persists for the lifetime of the task; the next hashed
bucket-0 enqueue dereferences it in io_wq_insert_work() and
wq_list_add_after() writes through freed memory.

Add the missing io_wq_is_hashed() check so a non-hashed predecessor
never inherits a hash_tail[] slot.

## References
- https://git.kernel.org/stable/c/252c5051dba9c709b6a72f2866f93e5e618b3f06
- https://git.kernel.org/stable/c/5a20ebf0c81b61f5ea3b1b529c100cad69b9f603
- https://git.kernel.org/stable/c/d376c131af7c7739a87ff037ed2fdb67c2542c8a
- https://git.kernel.org/stable/c/d6a2d7b04b5a093021a7a0e2e69e9d5237dfa8cc
- https://git.kernel.org/stable/c/d6bda9df0c0a3080804181464d5c0f4d78a4e769
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46274.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
