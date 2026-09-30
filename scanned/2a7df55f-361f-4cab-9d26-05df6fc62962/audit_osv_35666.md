# [H] Missing user-space pointer validation in logging syscall z_log_msg_static_create allows kernel memory disclosure and denial of service

## Summary
Severity: High
Advisory: CVE-2026-12364
Aliases: GHSA-h7rf-g9mg-g23f
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:H)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-12364
Type: osv

## Details
The user-space system-call verifier z_vrfy_z_log_msg_static_create() in subsys/logging/log_msg.c was a pure pass-through: it forwarded the caller-supplied source, desc, package, and data arguments directly to the kernel-mode implementation z_impl_z_log_msg_static_create() without performing any of the mandatory K_SYSCALL_* checks. Because z_log_msg_static_create() is declared __syscall, under CONFIG_USERSPACE any unprivileged user-mode thread can invoke it directly with fully attacker-controlled arguments.

The kernel-mode handler dereferences each of these untrusted values: frontend_runtime_filtering() reads through the source pointer as a struct log_source_dynamic_data, cbprintf_package_copy() reads desc.package_len bytes from the package pointer, and z_log_msg_finalize() performs a memcpy() of desc.data_len bytes from the data pointer. With no verification, a user thread can supply arbitrary kernel addresses and arbitrary lengths, and the kernel will read from them.

The impact is a kernel-mode denial of service (the kernel faults dereferencing an attacker-chosen pointer) and, where a log backend output is observable to the attacker, disclosure of arbitrary kernel memory copied into the emitted log message — a confidentiality breach across the user/kernel boundary that the userspace sandbox is meant to enforce. The reads do not corrupt kernel memory, so there is no out-of-bounds write primitive.

The fix adds the required validation to the verifier: it bounds desc.package_len against Z_LOG_MSG_MAX_PACKAGE, rejects non-NULL/length mismatches, and applies K_SYSCALL_MEMORY_READ() to package, data, and (when runtime filtering with a frontend is enabled) source, so any out-of-bounds or kernel pointer now raises K_OOPS instead of being honored.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12364.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-h7rf-g9mg-g23f
- https://nvd.nist.gov/vuln/detail/CVE-2026-12364
- https://github.com/zephyrproject-rtos/zephyr/commit/77aa26d8b940f39778154f02563caf15d02efdac
- https://github.com/zephyrproject-rtos/zephyr
