# [H] vsock: remove vsock from connected table when connect is interrupted by a signal

## Summary
Severity: High
Advisory: CVE-2022-48786
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48786
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <4.9.303, >=4.10.0 <4.14.268, >=4.15.0 <4.19.231, >=4.20.0 <5.4.181, >=5.5.0 <5.10.102, >=5.11.0 <5.15.25, >=5.16.0 <5.16.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock: remove vsock from connected table when connect is interrupted by a signal

vsock_connect() expects that the socket could already be in the
TCP_ESTABLISHED state when the connecting task wakes up with a signal
pending. If this happens the socket will be in the connected table, and
it is not removed when the socket state is reset. In this situation it's
common for the process to retry connect(), and if the connection is
successful the socket will be added to the connected table a second
time, corrupting the list.

Prevent this by calling vsock_remove_connected() if a signal is received
while waiting for a connection. This is harmless if the socket is not in
the connected table, and if it is in the table then removing it will
prevent list corruption from a double add.

Note for backporting: this patch requires d5afa82c977e ("vsock: correct
removal of socket from the list"), which is in all current stable trees
except 4.9.y.

## References
- https://git.kernel.org/stable/c/0bb88f3f7e8d506f3efe46d694964117e20efbfc
- https://git.kernel.org/stable/c/2910bcb9f67551a45397735e47b6d456eb8cd549
- https://git.kernel.org/stable/c/5f326fe2aef411a6575628f92bd861463ea91df7
- https://git.kernel.org/stable/c/787468ee7a435777521d33399d012fd591ae2f94
- https://git.kernel.org/stable/c/87cd1bbd6677411e17369cd4b7389ab1e1fdba44
- https://git.kernel.org/stable/c/addd62a8cb6fa90aa322365c62487da61f6baab8
- https://git.kernel.org/stable/c/b9208492fcaecff8f43915529ae34b3bcb03877c
- https://git.kernel.org/stable/c/e3b3939fd137aab6d00d54bee0ee9244b286a608
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48786.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48786
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
