# [M] Out-of-bounds write in Zephyr `log_filter_set` syscall verifier reachable from userspace

## Summary
Severity: Medium
Advisory: CVE-2026-10682
Aliases: GHSA-6vqh-mg7h-58qh
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-10682
Type: osv

## Details
The userspace verifier z_vrfy_log_filter_set() for the log_filter_set syscall in subsys/logging/log_mgmt.c performed a signed comparison against the int16_t src_id parameter: src_id < (int16_t)log_src_cnt_get(domain_id). Any negative value for src_id (e.g. -1) trivially satisfied this check and was forwarded into z_impl_log_filter_set, where it propagated to filter_set() and ultimately to get_dynamic_filter(), which uses source_id as an unsigned index into the linker-section array &TYPE_SECTION_START(log_dynamic)[source_id].filters.

After implicit conversion through uint32_t, an int16_t -1 becomes 0xFFFFFFFF, indexing log_dynamic far out of bounds and causing the kernel to perform an OOB read and an OOB read-modify-write (LOG_FILTER_SLOT_GET/SET) against memory adjacent to the log_dynamic section.

The written value is a constrained 3-bit log level slot within the targeted 32-bit word, but the target address is attacker-chosen (a small negative offset from log_dynamic) and the write occurs in supervisor mode following a syscall from an unprivileged user thread, providing a kernel memory-corruption / privilege-escalation primitive.

The defect is reachable on any build with CONFIG_USERSPACE=y and CONFIG_LOG_RUNTIME_FILTERING=y. Present from Zephyr v3.3.0 through v4.4.1. The fix replaces the signed bound check with an unsigned comparison: (uint32_t)src_id < log_src_cnt_get(domain_id), which correctly rejects negative inputs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10682.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-6vqh-mg7h-58qh
- https://nvd.nist.gov/vuln/detail/CVE-2026-10682
- https://github.com/zephyrproject-rtos/zephyr/commit/56a15114c6acbab2067fe406dc3adda8608f3def
- https://github.com/zephyrproject-rtos/zephyr
