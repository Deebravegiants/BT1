# [H] vsock: Do not allow binding to VMADDR_PORT_ANY

## Summary
Severity: High
Advisory: CVE-2025-38618
Aliases: A-439253642, ASB-A-439253642
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-22
Source: https://osv.dev/vulnerability/CVE-2025-38618
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.148, >=6.2.0 <6.6.102, >=6.7.0 <6.12.42, >=6.13.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock: Do not allow binding to VMADDR_PORT_ANY

It is possible for a vsock to autobind to VMADDR_PORT_ANY. This can
cause a use-after-free when a connection is made to the bound socket.
The socket returned by accept() also has port VMADDR_PORT_ANY but is not
on the list of unbound sockets. Binding it will result in an extra
refcount decrement similar to the one fixed in fcdd2242c023 (vsock: Keep
the binding until socket destruction).

Modify the check in __vsock_bind_connectible() to also prevent binding
to VMADDR_PORT_ANY.

## References
- https://git.kernel.org/stable/c/32950b1907919be86a7a2697d6f93d57068b3865
- https://git.kernel.org/stable/c/44bd006d5c93f6a8f28b106cbae2428c5d0275b7
- https://git.kernel.org/stable/c/8f01093646b49f6330bb2d36761983fd829472b1
- https://git.kernel.org/stable/c/aba0c94f61ec05315fa7815d21aefa4c87f6a9f4
- https://git.kernel.org/stable/c/c04a2c1ca25b9b23104124d3b2d349d934e302de
- https://git.kernel.org/stable/c/cf86704798c1b9c46fa59dfc2d662f57d1394d79
- https://git.kernel.org/stable/c/d1a5b1964cef42727668ac0d8532dae4f8c19386
- https://git.kernel.org/stable/c/d73960f0cf03ef1dc9e96ec7a20e538accc26d87
- https://git.kernel.org/stable/c/f138be5d7f301fddad4e65ec66dfc3ceebf79be3
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38618.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38618
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
