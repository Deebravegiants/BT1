# [M] SMP race in `thread_idx_alloc()` lets concurrent `k_object_alloc(K_OBJ_THREAD)` callers share a kernel-object permission slot

## Summary
Severity: Medium
Advisory: CVE-2026-10681
Aliases: GHSA-j693-5rh5-8g8h
CVSS: 6.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-10681
Type: osv

## Details
In Zephyr's userspace dynamic-objects subsystem, thread_idx_alloc() in kernel/userspace/userspace.c allocated a new thread permission index from the global _thread_idx_map[] bitmap without holding lists_lock.

On SMP systems, two user-mode threads invoking the k_object_alloc(K_OBJ_THREAD) syscall concurrently can both observe the same low free bit, perform the same non-atomic RMW to clear it, and return the identical tidx.

The two newly created K_OBJ_THREAD objects are then assigned the same thread_id, so the two user threads alias a single bit position in every kernel object's perms[] bitfield: any subsequent grant of access on a kernel object to one thread is implicitly a grant to the other, defeating userspace ACL isolation. A secondary lost-update window between the unlocked &=~BIT() in alloc and the locked |= BIT() in thread_idx_free() can also leak entries from the thread-index pool.

The defect is reachable from any user-mode thread via the unrestricted __syscall k_object_alloc and is gated on CONFIG_USERSPACE, CONFIG_DYNAMIC_OBJECTS, and CONFIG_SMP. The flaw was introduced when the per-thread permission index was added in 2018 and is present in every release up to and including v4.4.0. Fixed by holding lists_lock across the bitmap RMW and the permissions clear (and inlining the obj_list traversal that previously took the lock itself).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10681.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-j693-5rh5-8g8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-10681
- https://github.com/zephyrproject-rtos/zephyr/commit/862ea2fbbeb2ccdf8ff994b03e2e3b4405f2c37d
- https://github.com/zephyrproject-rtos/zephyr
