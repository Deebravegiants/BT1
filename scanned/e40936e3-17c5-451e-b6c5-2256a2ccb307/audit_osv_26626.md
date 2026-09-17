# [H] xsk: Fix xsk_diag use-after-free error during socket cleanup

## Summary
Severity: High
Advisory: CVE-2023-53426
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53426
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.132, >=5.16.0 <6.1.54, >=5.18.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: Fix xsk_diag use-after-free error during socket cleanup

Fix a use-after-free error that is possible if the xsk_diag interface
is used after the socket has been unbound from the device. This can
happen either due to the socket being closed or the device
disappearing. In the early days of AF_XDP, the way we tested that a
socket was not bound to a device was to simply check if the netdevice
pointer in the xsk socket structure was NULL. Later, a better system
was introduced by having an explicit state variable in the xsk socket
struct. For example, the state of a socket that is on the way to being
closed and has been unbound from the device is XSK_UNBOUND.

The commit in the Fixes tag below deleted the old way of signalling
that a socket is unbound, setting dev to NULL. This in the belief that
all code using the old way had been exterminated. That was
unfortunately not true as the xsk diagnostics code was still using the
old way and thus does not work as intended when a socket is going
down. Fix this by introducing a test against the state variable. If
the socket is in the state XSK_UNBOUND, simply abort the diagnostic's
netlink operation.

## References
- https://git.kernel.org/stable/c/3e019d8a05a38abb5c85d4f1e85fda964610aa14
- https://git.kernel.org/stable/c/595931912357fa3507e522a7f8a0a76e423c23e4
- https://git.kernel.org/stable/c/5979985f2d6b565b6cf0f79a62670a2855c0e96c
- https://git.kernel.org/stable/c/6436973164ea5506a495f39e56be5aea375e7832
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53426.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53426
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
