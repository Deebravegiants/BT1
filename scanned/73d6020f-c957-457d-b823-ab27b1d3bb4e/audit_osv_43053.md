# [H] sctp: fix addr_wq_timer race in sctp_free_addr_wq()

## Summary
Severity: High
Advisory: CVE-2026-72383
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72383
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: fix addr_wq_timer race in sctp_free_addr_wq()

sctp_free_addr_wq() previously removed addr_wq_timer using timer_delete()
while holding addr_wq_lock. However, timer_delete() does not guarantee that
a currently running timer handler has completed.

This allows a race with sctp_addr_wq_timeout_handler(), where the handler
may still run after addr_waitq has been freed, acquire addr_wq_lock, and
access freed memory, leading to a use-after-free.

Fix this by calling timer_shutdown_sync() before taking addr_wq_lock.  This
guarantees that any in-flight timer handler has finished and prevents the
timer from being re-armed during teardown, making subsequent cleanup safe.

## References
- https://git.kernel.org/stable/c/976c19de0f22a857ba0112f39635f8fd7a257568
- https://git.kernel.org/stable/c/a8323fb2ab6cd6978f359daeed6688e0cadf32ba
- https://git.kernel.org/stable/c/c3e5cac47519d77ad36b9c03a1df1536aaa0c4a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72383.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
