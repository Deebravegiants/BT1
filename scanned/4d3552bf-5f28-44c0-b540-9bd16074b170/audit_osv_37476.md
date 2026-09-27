# [H] openvswitch: defer tunnel netdev_put to RCU release

## Summary
Severity: High
Advisory: CVE-2026-31678
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31678
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

openvswitch: defer tunnel netdev_put to RCU release

ovs_netdev_tunnel_destroy() may run after NETDEV_UNREGISTER already
detached the device. Dropping the netdev reference in destroy can race
with concurrent readers that still observe vport->dev.

Do not release vport->dev in ovs_netdev_tunnel_destroy(). Instead, let
vport_netdev_free() drop the reference from the RCU callback, matching
the non-tunnel destroy path and avoiding additional synchronization
under RTNL.

## References
- https://git.kernel.org/stable/c/42f0d3d81209654c08ffdde5a34b9b92d2645896
- https://git.kernel.org/stable/c/6931d21f87bc6d657f145798fad0bf077b82486c
- https://git.kernel.org/stable/c/98b726ab5e2a4811e27c28e4d041f75bba147eab
- https://git.kernel.org/stable/c/9d56aced21fb9c104e8a3f3be9b21fbafe448ffc
- https://git.kernel.org/stable/c/b8c56a3fc5d879c0928f207a756b0f067f06c6a8
- https://git.kernel.org/stable/c/bbe7bd722bfaea36aab3da6cc60fb4a05c644643
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31678.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31678
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
