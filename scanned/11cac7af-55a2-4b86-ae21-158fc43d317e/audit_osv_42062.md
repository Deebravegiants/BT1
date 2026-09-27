# [H] net: ipv4: bound TCP reordering sysctl writes and MTU probe sizes

## Summary
Severity: High
Advisory: CVE-2026-64422
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64422
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ipv4: bound TCP reordering sysctl writes and MTU probe sizes

Reject invalid `net.ipv4.tcp_reordering` values before they reach TCP
socket state. The sysctl is stored as an `int` but copied into the
`u32` `tp->reordering` field for new sockets, so negative writes wrap
to large values.

With `tcp_mtu_probing=2`, the wrapped value can overflow the
`tcp_mtu_probe()` size calculation and drive the MTU probing path into
an out-of-bounds read. Route `tcp_reordering` writes through
`proc_dointvec_minmax()` and require it to be at least 1. Also require
`tcp_max_reordering` to be at least 1 so the configured maximum cannot
become negative either.

When registering the table for a non-init network namespace, relocate
`extra2` pointers that refer into `init_net.ipv4` so the
`tcp_reordering` upper bound follows that namespace's
`tcp_max_reordering`.

Harden `tcp_mtu_probe()` itself by computing `size_needed` as `u64`.
This keeps the send queue and window checks from being bypassed through
signed integer overflow.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/27ddf4486c7dbf5bdd393fa8bef6b67179796d98
- https://git.kernel.org/stable/c/782708ca1ea1f68b8cbb5ea3a7f5f18d0000efae
- https://git.kernel.org/stable/c/99206ce2244f8a3ed64298d0667c9055845a5dc7
- https://git.kernel.org/stable/c/a094ac95d3b69adfa1676eb9c8eae6835d4f1671
- https://git.kernel.org/stable/c/bbae351c0f32f7c200249e4aa6561b2b419dcf69
- https://git.kernel.org/stable/c/e81f805824a8109504fce090641b17d135b48cd1
- https://git.kernel.org/stable/c/efb8763d7bbb40cff4cc55a6b62c3095a038149c
- https://git.kernel.org/stable/c/f0d88a4cd03affff6c08adf6c63964e235aede43
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64422.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64422
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
