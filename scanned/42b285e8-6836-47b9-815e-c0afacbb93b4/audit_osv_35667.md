# [M] Use-after-free in Zephyr delayable work-queue cancellation under SMP timing race

## Summary
Severity: Medium
Advisory: CVE-2026-12365
Aliases: GHSA-rhmh-r93p-6g99
CVSS: 5.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-12365
Type: osv

## Details
A use-after-free exists in the Zephyr second-generation work queue (kernel/work.c) in the handling of delayable work timeouts. When a delayable work item's timeout has been dequeued and its handler work_timeout() is in flight (blocked acquiring the work-queue spinlock), a concurrent cancellation does not wait for that handler to finish. In unschedule_locked() the pre-fix code called z_abort_timeout(), which for an already-announcing record returns -EINVAL without removing it; cancel_async_locked() then observes the work as idle, so even k_work_cancel_delayable_sync() and k_work_flush_delayable() return without blocking on the in-flight handler.

Because those are the APIs the kernel header documents as the safe way to cancel before freeing a k_work_delayable, a caller that frees the object immediately after a successful sync cancel can race the still-pending handler. work_timeout() subsequently dereferences the freed record: it reads to->dticks via z_is_timeout_handler_canceled() and, if the freed slot has been reused so the bail check fails, performs a read-modify-write of wp->flags (K_WORK_DELAYED_BIT) and submits work against a stale dw->queue pointer — a use-after-free read and write.

The k_work API is kernel-mode only (no __syscall entry point), so this is a kernel-internal concurrency defect rather than a userspace privilege escalation. Triggering it requires an SMP build and a subsystem that schedules and then frees (or reschedules) a delayable work item in the narrow window while its timeout is announcing; an attacker able to influence the timing of such teardown (for example via connection churn driving subsystem timers) has a plausible but probabilistic path. The impact is kernel memory corruption or crash (denial of service).

The fix makes unschedule_locked() wait, by spinning on z_try_abort_timeout() returning -EAGAIN while releasing and re-acquiring the work spinlock, until any in-flight handler completes before returning, and switches work_timeout() to atomic K_WORK_DELAYED_BIT ownership. This closes both the free-then-handler use-after-free and the related reschedule early-fire race.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12365.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-rhmh-r93p-6g99
- https://nvd.nist.gov/vuln/detail/CVE-2026-12365
- https://github.com/zephyrproject-rtos/zephyr/commit/59cf34bf212eeb5c7ea88b97e15842b1e7c1a6b7
- https://github.com/zephyrproject-rtos/zephyr
