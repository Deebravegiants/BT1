# [M] User-triggerable kernel NULL-pointer dereference (DoS) in `k_thread_name_copy()` syscall verifier

## Summary
Severity: Medium
Advisory: CVE-2026-10670
Aliases: GHSA-82h2-v4vm-q2g9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-10670
Type: osv

## Details
The CONFIG_USERSPACE verification handler for the k_thread_name_copy() system call (z_vrfy_k_thread_name_copy() in kernel/thread.c) calls k_object_find() on the caller-supplied thread pointer and then dereferences the returned struct k_object without checking it for NULL. k_object_find() returns NULL whenever the supplied pointer is not a registered (static or dynamic) kernel object.

The pre-fix guard tested thread == NULL instead of ko == NULL, so an unprivileged user-mode thread that invokes k_thread_name_copy() with any non-NULL but unregistered pointer (e.g. an arbitrary address) passes the NULL test, after which the verifier reads ko->type through a NULL pointer.

Because the syscall verifier runs in supervisor mode, this NULL dereference is a kernel-mode fault that halts or reboots the system, allowing untrusted user code to crash the kernel across the userspace security boundary (denial of service). The marshaller passes the thread argument to the verifier without any prior K_SYSCALL_OBJ validation, so the bad pointer reaches the defect directly.

The flaw affects builds with CONFIG_USERSPACE and CONFIG_THREAD_NAME enabled and has been present since the special-case lookup was introduced around v2.0.0; it is present in v4.4.0 and earlier. The fix changes the guard to check the k_object_find() return value (ko == NULL) before dereferencing it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10670.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-82h2-v4vm-q2g9
- https://nvd.nist.gov/vuln/detail/CVE-2026-10670
- https://github.com/zephyrproject-rtos/zephyr/commit/491583951036bc5794a3843a4baa246453bb1ee2
- https://github.com/zephyrproject-rtos/zephyr
