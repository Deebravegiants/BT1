# [C] ksmbd: fix use-after-free in SMB request handling

## Summary
Severity: Critical
Advisory: CVE-2024-53186
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53186
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in SMB request handling

A race condition exists between SMB request handling in
`ksmbd_conn_handler_loop()` and the freeing of `ksmbd_conn` in the
workqueue handler `handle_ksmbd_work()`. This leads to a UAF.
- KASAN: slab-use-after-free Read in handle_ksmbd_work
- KASAN: slab-use-after-free in rtlock_slowlock_locked

This race condition arises as follows:
- `ksmbd_conn_handler_loop()` waits for `conn->r_count` to reach zero:
  `wait_event(conn->r_count_q, atomic_read(&conn->r_count) == 0);`
- Meanwhile, `handle_ksmbd_work()` decrements `conn->r_count` using
  `atomic_dec_return(&conn->r_count)`, and if it reaches zero, calls
  `ksmbd_conn_free()`, which frees `conn`.
- However, after `handle_ksmbd_work()` decrements `conn->r_count`,
  it may still access `conn->r_count_q` in the following line:
  `waitqueue_active(&conn->r_count_q)` or `wake_up(&conn->r_count_q)`
  This results in a UAF, as `conn` has already been freed.

The discovery of this UAF can be referenced in the following PR for
syzkaller's support for SMB requests.

## References
- https://git.kernel.org/stable/c/96261adb998a3b513468b6ce17dbec76be5507d4
- https://git.kernel.org/stable/c/9a8c5d89d327ff58e9b2517f8a6afb4181d32c6e
- https://git.kernel.org/stable/c/a96f9eb7add30ba0fafcfe7b7aca090978196800
- https://git.kernel.org/stable/c/f20b77f7897e6aab9ce5527e6016ad2be5d70a33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53186.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
