# [H] User thread can re-initialize an in-use `k_pipe`, corrupting kernel wait queues (`CONFIG_USERSPACE`)

## Summary
Severity: High
Advisory: CVE-2026-10671
Aliases: GHSA-p8w8-3x99-mg8f
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-10671
Type: osv

## Details
In Zephyr's kernel pipe implementation, the userspace syscall verifier z_vrfy_k_pipe_init() in kernel/pipe.c used K_SYSCALL_OBJ() (which requires the kernel object to already be initialized) instead of K_SYSCALL_OBJ_NEVER_INIT() (which rejects an already-initialized object). As a result, on CONFIG_USERSPACE builds an unprivileged user thread that has been granted access to a k_pipe object can invoke the k_pipe_init syscall to re-initialize a pipe that is already in use.

z_impl_k_pipe_init() unconditionally resets the ring buffer, sets pipe->waiting to 0, and re-initializes both wait queues (z_waitq_init on pipe->data and pipe->space) without waking or accounting for threads currently blocked on the pipe. Any thread already pended in k_pipe_read()/k_pipe_write() is left orphaned: still marked pending with pended_on pointing at the cleared wait queue and with stale qnode_dlist links into the (now re-initialized) embedded list head.

When such an orphaned waiter is later timed out or woken, the scheduler calls sys_dlist_remove() on its stale node, writing through dangling prev/next pointers into kernel wait-queue/scheduler structures, causing list corruption (an attacker-driven invalid kernel write), lost wakeups, indefinitely blocked threads, and silent data loss. The flaw lets a deprivileged user thread corrupt the state of a kernel object shared with other threads/partitions.

The fix switches the verifier to K_SYSCALL_OBJ_NEVER_INIT(), matching the existing k_msgq_init verifier, so a user thread can no longer re-initialize a live pipe. The vulnerable code shipped in v4.1.0 and remained through v4.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10671.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-p8w8-3x99-mg8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-10671
- https://github.com/zephyrproject-rtos/zephyr/commit/4424aa681e0b80e9cbd0ae27a987d582be88cb74
- https://github.com/zephyrproject-rtos/zephyr
