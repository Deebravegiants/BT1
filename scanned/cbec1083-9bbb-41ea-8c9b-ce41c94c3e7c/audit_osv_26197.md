# [C] ksmbd: fix race condition between session lookup and expire

## Summary
Severity: Critical
Advisory: CVE-2023-52480
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-52480
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.57, >=6.2.0 <6.5.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix race condition between session lookup and expire

 Thread A                        +  Thread B
 ksmbd_session_lookup            |  smb2_sess_setup
   sess = xa_load                |
                                 |
                                 |    xa_erase(&conn->sessions, sess->id);
                                 |
                                 |    ksmbd_session_destroy(sess) --> kfree(sess)
                                 |
   // UAF!                       |
   sess->last_active = jiffies   |
                                 +

This patch add rwsem to fix race condition between ksmbd_session_lookup
and ksmbd_expire_session.

## References
- https://git.kernel.org/stable/c/18ced78b0ebccc2d16f426143dc56ab3aad666be
- https://git.kernel.org/stable/c/53ff5cf89142b978b1a5ca8dc4d4425e6a09745f
- https://git.kernel.org/stable/c/a2ca5fd3dbcc665e1169044fa0c9e3eba779202b
- https://git.kernel.org/stable/c/c77fd3e25a51ac92b0f1b347a96eff6a0b4f066f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52480.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52480
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
