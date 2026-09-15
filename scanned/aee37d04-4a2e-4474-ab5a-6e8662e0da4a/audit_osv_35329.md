# [H] ublk: clean up user copy references on ublk server exit

## Summary
Severity: High
Advisory: CVE-2025-71070
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71070
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ublk: clean up user copy references on ublk server exit

If a ublk server process releases a ublk char device file, any requests
dispatched to the ublk server but not yet completed will retain a ref
value of UBLK_REFCOUNT_INIT. Before commit e63d2228ef83 ("ublk: simplify
aborting ublk request"), __ublk_fail_req() would decrement the reference
count before completing the failed request. However, that commit
optimized __ublk_fail_req() to call __ublk_complete_rq() directly
without decrementing the request reference count.
The leaked reference count incorrectly allows user copy and zero copy
operations on the completed ublk request. It also triggers the
WARN_ON_ONCE(refcount_read(&io->ref)) warnings in ublk_queue_reinit()
and ublk_deinit_queue().
Commit c5c5eb24ed61 ("ublk: avoid ublk_io_release() called after ublk
char dev is closed") already fixed the issue for ublk devices using
UBLK_F_SUPPORT_ZERO_COPY or UBLK_F_AUTO_BUF_REG. However, the reference
count leak also affects UBLK_F_USER_COPY, the other reference-counted
data copy mode. Fix the condition in ublk_check_and_reset_active_ref()
to include all reference-counted data copy modes. This ensures that any
ublk requests still owned by the ublk server when it exits have their
reference counts reset to 0.

## References
- https://git.kernel.org/stable/c/13456b4f1033d911f8bf3a0a1195656f293ba0f6
- https://git.kernel.org/stable/c/daa24603d9f0808929514ee62ced30052ca7221c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71070.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71070
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
