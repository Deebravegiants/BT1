# [C] mptcp: fix slab-use-after-free in __inet_lookup_established

## Summary
Severity: Critical
Advisory: CVE-2026-31669
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31669
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix slab-use-after-free in __inet_lookup_established

The ehash table lookups are lockless and rely on
SLAB_TYPESAFE_BY_RCU to guarantee socket memory stability
during RCU read-side critical sections. Both tcp_prot and
tcpv6_prot have their slab caches created with this flag
via proto_register().

However, MPTCP's mptcp_subflow_init() copies tcpv6_prot into
tcpv6_prot_override during inet_init() (fs_initcall, level 5),
before inet6_init() (module_init/device_initcall, level 6) has
called proto_register(&tcpv6_prot). At that point,
tcpv6_prot.slab is still NULL, so tcpv6_prot_override.slab
remains NULL permanently.

This causes MPTCP v6 subflow child sockets to be allocated via
kmalloc (falling into kmalloc-4k) instead of the TCPv6 slab
cache. The kmalloc-4k cache lacks SLAB_TYPESAFE_BY_RCU, so
when these sockets are freed without SOCK_RCU_FREE (which is
cleared for child sockets by design), the memory can be
immediately reused. Concurrent ehash lookups under
rcu_read_lock can then access freed memory, triggering a
slab-use-after-free in __inet_lookup_established.

Fix this by splitting the IPv6-specific initialization out of
mptcp_subflow_init() into a new mptcp_subflow_v6_init(), called
from mptcp_proto_v6_init() before protocol registration. This
ensures tcpv6_prot_override.slab correctly inherits the
SLAB_TYPESAFE_BY_RCU slab cache.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/15fa9ead4d5e6b6b9c794e84144146c917f2cb62
- https://git.kernel.org/stable/c/3fd6547f5b8ac99687be6d937a0321efda760597
- https://git.kernel.org/stable/c/9b55b253907e7431210483519c5ad711a37dafa1
- https://git.kernel.org/stable/c/b313e9037d98c13938740e5ebda7852929366dff
- https://git.kernel.org/stable/c/eb9c6aeb512f877cf397deb1e4526f646c70e4a7
- https://git.kernel.org/stable/c/f6e1f25fa5e733570f6d6fe37a4dfed2a0deba47
- https://git.kernel.org/stable/c/fb1f54b7d16f393b8b65d328410f78b4beea8fcc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31669.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
