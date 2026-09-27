# [M] Broken access-control denial in k_thread_join/k_thread_abort syscall validation in Zephyr kernel

## Summary
Severity: Medium
Advisory: CVE-2026-12631
Aliases: GHSA-crfw-75jw-hjm3
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-12631
Type: osv

## Details
The Zephyr kernel validates the k_thread_join() and k_thread_abort() system calls (declared __syscall in include/zephyr/kernel.h) through thread_obj_validate() in kernel/thread.c. Its default switch branch is the access-denied path, taken when k_object_validate() returns -EPERM (the calling user thread was never granted access to the target thread object) or -EBADF (the supplied pointer is not a registered kernel object of the right type). That branch invoked K_OOPS(K_SYSCALL_VERIFY_MSG(ret, "access denied")), but K_SYSCALL_VERIFY_MSG treats a true expression as success; the non-zero error code ret therefore read as "verified OK", the kernel oops was never raised, and control fell through to CODE_UNREACHABLE.

Because k_thread_join() and k_thread_abort() are system calls, an unprivileged user-mode thread (under CONFIG_USERSPACE) can reach this denial path directly by calling either syscall on a thread object it does not own. Instead of the offending thread being cleanly terminated, execution reaches __builtin_unreachable() while running in supervisor mode inside the syscall handler.

On Clang builds CODE_UNREACHABLE emits an illegal-instruction trap, so a user thread can deterministically crash the kernel — a locally triggerable denial of service that escapes the userspace sandbox. On GCC builds the path is undefined behavior: the compiler may drop the return-value handling for thread_obj_validate(), so it can return an undefined bool; if that is false, the caller proceeds into the real k_thread_join()/k_thread_abort() implementation for a thread the user was never authorized to access, an access-control bypass.

The fix changes the verification expression to ret == 0, so a denied (non-zero) result now correctly raises K_OOPS and terminates the offending caller.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12631.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-crfw-75jw-hjm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-12631
- https://github.com/zephyrproject-rtos/zephyr/commit/bd1828652dfc217ba9f3a2221a7499cd8914ed9c
- https://github.com/zephyrproject-rtos/zephyr
