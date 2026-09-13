# [H] scsi: target: iscsi: Fix use-after-free in iscsit_dec_session_usage_count()

## Summary
Severity: High
Advisory: CVE-2026-23193
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23193
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.1.0 <5.10.250, >=5.11.0 <5.15.200, >=5.16.0 <6.1.163, >=6.2.0 <6.6.124, >=6.7.0 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: target: iscsi: Fix use-after-free in iscsit_dec_session_usage_count()

In iscsit_dec_session_usage_count(), the function calls complete() while
holding the sess->session_usage_lock. Similar to the connection usage count
logic, the waiter signaled by complete() (e.g., in the session release
path) may wake up and free the iscsit_session structure immediately.

This creates a race condition where the current thread may attempt to
execute spin_unlock_bh() on a session structure that has already been
deallocated, resulting in a KASAN slab-use-after-free.

To resolve this, release the session_usage_lock before calling complete()
to ensure all dereferences of the sess pointer are finished before the
waiter is allowed to proceed with deallocation.

## References
- https://git.kernel.org/stable/c/11ebafffce31efc6abeb28c509017976fc49f1ca
- https://git.kernel.org/stable/c/2b64015550a13bcc72910be0565548d9a754d46d
- https://git.kernel.org/stable/c/41b86a9ec037bd3435d68dd3692f0891a207e7e7
- https://git.kernel.org/stable/c/4530f4e4d0e6a207110b0ffed0c911bca43531a4
- https://git.kernel.org/stable/c/84dc6037390b8607c5551047d3970336cb51ba9a
- https://git.kernel.org/stable/c/d8dbdc146e9e9a976931b78715be2e91299049f9
- https://git.kernel.org/stable/c/fd8b0900173307039d3a84644c2fee041a7ed4fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23193.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23193
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
