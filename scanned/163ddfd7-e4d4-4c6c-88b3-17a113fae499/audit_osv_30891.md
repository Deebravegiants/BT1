# [H] sunrpc: clear XPRT_SOCK_UPD_TIMEOUT when reset transport

## Summary
Severity: High
Advisory: CVE-2024-56688
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56688
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

sunrpc: clear XPRT_SOCK_UPD_TIMEOUT when reset transport

Since transport->sock has been set to NULL during reset transport,
XPRT_SOCK_UPD_TIMEOUT also needs to be cleared. Otherwise, the
xs_tcp_set_socket_timeouts() may be triggered in xs_tcp_send_request()
to dereference the transport->sock that has been set to NULL.

## References
- https://git.kernel.org/stable/c/3811172e8c98ceebd12fe526ca6cb37a1263c964
- https://git.kernel.org/stable/c/4db9ad82a6c823094da27de4825af693a3475d51
- https://git.kernel.org/stable/c/638a8fa5a7e641f9401346c57e236f02379a0c40
- https://git.kernel.org/stable/c/66d11ca91bf5100ae2e6b5efad97e58d8448843a
- https://git.kernel.org/stable/c/86a1f9fa24804cd7f9d7dd3f24af84fc7f8ec02e
- https://git.kernel.org/stable/c/87a95ee34a48dfad198a2002e4966e1d63d53f2b
- https://git.kernel.org/stable/c/cc91d59d34ff6a6fee1c0b48612081a451e05e9a
- https://git.kernel.org/stable/c/fe6cbf0b2ac3cf4e21824a44eaa336564ed5e960
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56688.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56688
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
