# [M] TOCTOU race in mbox_send syscall verifier allows userspace to leak kernel memory

## Summary
Severity: Medium
Advisory: CVE-2026-9728
Aliases: GHSA-47q2-w832-7w67
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:L)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-9728
Type: osv

## Details
The userspace syscall verifier z_vrfy_mbox_send() in drivers/mbox/mbox_handlers.c validated the nested msg->data/msg->size fields by reading them directly out of live userspace memory, and then forwarded the original, still-mutable userspace struct mbox_msg * pointer to z_impl_mbox_send() and the underlying driver. Between the access check and the driver's use of msg->data, the validated pointer could be replaced, leaving a time-of-check/time-of-use window.

On a system built with CONFIG_USERSPACE, any unprivileged userspace thread may invoke the mbox_send() system call. A second thread sharing the caller's address space can race to overwrite msg->data with a supervisor (kernel) address after the verifier's bounds check has passed but before the driver dereferences it. The driver then reads from the attacker-chosen address in supervisor context (for example memcpy(&data32, msg->data, msg->size) in the NXP mailbox driver, whose bytes are subsequently emitted to the peer mailbox endpoint).

The impact is a userspace-to-supervisor access-control bypass: disclosure of kernel memory contents (high confidentiality impact), or, for an invalid/unmapped target address, a faulting kernel read causing denial of service. The fix snapshots the entire struct mbox_msg into a kernel-stack copy with k_usermode_from_copy() and validates and forwards that immutable copy, closing the race.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9728.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-47q2-w832-7w67
- https://nvd.nist.gov/vuln/detail/CVE-2026-9728
- https://github.com/zephyrproject-rtos/zephyr/commit/ab35eaccec5976f05c196f176d0c32885754496f
- https://github.com/zephyrproject-rtos/zephyr
