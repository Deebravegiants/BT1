# [H] ksmbd: fix use-after-free in __smb2_lease_break_noti()

## Summary
Severity: High
Advisory: CVE-2025-37777
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37777
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.6.101, >=6.7.0 <6.12.26, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in __smb2_lease_break_noti()

Move tcp_transport free to ksmbd_conn_free. If ksmbd connection is
referenced when ksmbd server thread terminates, It will not be freed,
but conn->tcp_transport is freed. __smb2_lease_break_noti can be performed
asynchronously when the connection is disconnected. __smb2_lease_break_noti
calls ksmbd_conn_write, which can cause use-after-free
when conn->ksmbd_transport is already freed.

## References
- https://git.kernel.org/stable/c/1aec4d14cf81b7b3e7b69eb1cfa94144eed7138e
- https://git.kernel.org/stable/c/1da8bd9a10ecd718692732294d15fd801c0eabb5
- https://git.kernel.org/stable/c/21a4e47578d44c6b37c4fc4aba8ed7cc8dbb13de
- https://git.kernel.org/stable/c/e59796fc80603bcd8569d4d2e10b213c1918edb4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37777.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37777
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
