# [M] netlabel: Fix NULL pointer exception caused by CALIPSO on IPv4 sockets

## Summary
Severity: Medium
Advisory: CVE-2025-22063
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22063
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netlabel: Fix NULL pointer exception caused by CALIPSO on IPv4 sockets

When calling netlbl_conn_setattr(), addr->sa_family is used
to determine the function behavior. If sk is an IPv4 socket,
but the connect function is called with an IPv6 address,
the function calipso_sock_setattr() is triggered.
Inside this function, the following code is executed:

sk_fullsock(__sk) ? inet_sk(__sk)->pinet6 : NULL;

Since sk is an IPv4 socket, pinet6 is NULL, leading to a
null pointer dereference.

This patch fixes the issue by checking if inet6_sk(sk)
returns a NULL pointer before accessing pinet6.

## References
- https://git.kernel.org/stable/c/078aabd567de3d63d37d7673f714e309d369e6e2
- https://git.kernel.org/stable/c/172a8a996a337206970467e871dd995ac07640b1
- https://git.kernel.org/stable/c/1927d0bcd5b81e80971bf6b8eba267508bd1c78b
- https://git.kernel.org/stable/c/1ad9166cab6a0f5c0b10344a97bdf749ae11dcbf
- https://git.kernel.org/stable/c/1e38f7a6cdd68377f8a4189b2fbaec14a6dd5152
- https://git.kernel.org/stable/c/3ba9cf69de50e8abed32b448616c313baa4c5712
- https://git.kernel.org/stable/c/797e5371cf55463b4530bab3fef5f27f7c6657a8
- https://git.kernel.org/stable/c/9fe3839588db7519030377b7dee3f165e654f6c5
- https://git.kernel.org/stable/c/a7e89541d05b98c79a51c0f95df020f8e82b62ed
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22063.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22063
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
