# [H] nilfs2: fix potential UAF of struct nilfs_sc_info in nilfs_segctor_thread()

## Summary
Severity: High
Advisory: CVE-2023-53608
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53608
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.14.313, >=4.15.0 <4.19.281, >=4.20.0 <5.4.241, >=5.5.0 <5.10.178, >=5.11.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix potential UAF of struct nilfs_sc_info in nilfs_segctor_thread()

The finalization of nilfs_segctor_thread() can race with
nilfs_segctor_kill_thread() which terminates that thread, potentially
causing a use-after-free BUG as KASAN detected.

At the end of nilfs_segctor_thread(), it assigns NULL to "sc_task" member
of "struct nilfs_sc_info" to indicate the thread has finished, and then
notifies nilfs_segctor_kill_thread() of this using waitqueue
"sc_wait_task" on the struct nilfs_sc_info.

However, here, immediately after the NULL assignment to "sc_task", it is
possible that nilfs_segctor_kill_thread() will detect it and return to
continue the deallocation, freeing the nilfs_sc_info structure before the
thread does the notification.

This fixes the issue by protecting the NULL assignment to "sc_task" and
its notification, with spinlock "sc_state_lock" of the struct
nilfs_sc_info.  Since nilfs_segctor_kill_thread() does a final check to
see if "sc_task" is NULL with "sc_state_lock" locked, this can eliminate
the race.

## References
- https://git.kernel.org/stable/c/034cce77d52ba013ce62b4f5258c29907eb1ada5
- https://git.kernel.org/stable/c/0dbf0e64b91ee8fcb278aea93eb06fc7d56ecbcc
- https://git.kernel.org/stable/c/613bf23c070d11c525268f2945aa594704a9b764
- https://git.kernel.org/stable/c/6be49d100c22ffea3287a4b19d7639d259888e33
- https://git.kernel.org/stable/c/92684e02654c91a61a0b0561433b710bcece19fe
- https://git.kernel.org/stable/c/b4d80bd6370b81a1725b6b8f7894802c23a14e9f
- https://git.kernel.org/stable/c/bae009a2f1b7c2011d2e92d8c84868d315c0b97e
- https://git.kernel.org/stable/c/f32297dba338dc06d62286dedb3cdbd5175b1719
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53608.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53608
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
