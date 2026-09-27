# [H] Bluetooth: ISO: hold sk properly in iso_conn_ready

## Summary
Severity: High
Advisory: CVE-2026-74537
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74537
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: ISO: hold sk properly in iso_conn_ready

sk deref in iso_conn_ready must be done either under conn->lock, or
holding a refcount, to avoid concurrent close. conn->sk is currently
accessed without either:

    [Task 1]            [Task 2]
                        iso_sock_release
    iso_conn_ready
      sk = conn->sk
                          lock_sock(sk)
                            conn->sk = NULL
      lock_sock(sk)
                          release_sock(sk)
                          iso_sock_kill(sk)
       UAF on sk deref

Fix possible UAF by holding sk refcount in iso_conn_ready().  Also
recheck after lock_sock that the socket is still valid.  Adjust locking
so conn->sk is cleared only under lock_sock.

## References
- https://git.kernel.org/stable/c/0d255e63fcf3f13a570d7ac11678fa1164ac015c
- https://git.kernel.org/stable/c/1308d72903d792d10b82bc4ef08b8a4452308b04
- https://git.kernel.org/stable/c/4e9b5e8669b3602a4e01b6d1e9539b72e42c84d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74537.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74537
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
