# [M] Kernel heap memory leak in `z_vrfy_k_poll()` lets an unprivileged user thread exhaust the kernel resource pool

## Summary
Severity: Medium
Advisory: CVE-2026-10677
Aliases: GHSA-r3cc-8wcr-xfj9
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-10677
Type: osv

## Details
The CONFIG_USERSPACE syscall verifier z_vrfy_k_poll() in kernel/poll.c allocates a kernel-side copy of the user-supplied k_poll_event[] via z_thread_malloc() and then validates each event's object handle. Before this fix, validation used K_OOPS(K_SYSCALL_OBJ(...)) inline inside the loop, which kills the calling thread without freeing events_copy.

A user thread can pass num_events >= 1 with a forged object handle to leak the allocation; because newly spawned user threads inherit the parent's resource_pool (kernel/thread.c), an attacker spawns sacrificial threads to repeat the leak until the shared kernel heap is exhausted. Once depleted, legitimate kernel allocations from that pool (k_queue alloc nodes, k_msgq buffers, future k_poll calls, etc.) fail, causing a system-level denial of service.

The fix replaces each inline K_OOPS with a conditional goto oops_free so the buffer is freed before the thread is killed. Affects Zephyr releases from v1.12.0 (when k_poll was first exposed to user mode) through v4.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10677.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-r3cc-8wcr-xfj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-10677
- https://github.com/zephyrproject-rtos/zephyr/commit/8dc7a37bc75402a0a3329397887f32f5fb4da3ad
- https://github.com/zephyrproject-rtos/zephyr
