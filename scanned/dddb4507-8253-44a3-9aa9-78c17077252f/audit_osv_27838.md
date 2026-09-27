# [C] ksmbd: fix UAF issue in ksmbd_tcp_new_connection()

## Summary
Severity: Critical
Advisory: CVE-2024-26592
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2024-26592
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.149, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix UAF issue in ksmbd_tcp_new_connection()

The race is between the handling of a new TCP connection and
its disconnection. It leads to UAF on `struct tcp_transport` in
ksmbd_tcp_new_connection() function.

## References
- https://git.kernel.org/stable/c/24290ba94cd0136e417283b0dbf8fcdabcf62111
- https://git.kernel.org/stable/c/380965e48e9c32ee4263c023e1d830ea7e462ed1
- https://git.kernel.org/stable/c/38d20c62903d669693a1869aa68c4dd5674e2544
- https://git.kernel.org/stable/c/69d54650b751532d1e1613a4fb433e591aeef126
- https://git.kernel.org/stable/c/999daf367b924fdf14e9d83e034ee0f86bc17ec6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26592.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26592
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
