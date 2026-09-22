# [H] tipc: require net admin for TIPCv2 netlink mutators

## Summary
Severity: High
Advisory: CVE-2026-74283
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74283
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: require net admin for TIPCv2 netlink mutators

TIPCv2 registers mutating generic-netlink operations without admin
permission flags. Generic netlink only checks CAP_NET_ADMIN when an
operation sets GENL_ADMIN_PERM or GENL_UNS_ADMIN_PERM, so a local
unprivileged process can currently change TIPC state through commands
such as TIPC_NL_NET_SET, TIPC_NL_KEY_SET, TIPC_NL_KEY_FLUSH, and
bearer enable/disable.

The legacy TIPC netlink API already checks netlink_net_capable(...,
CAP_NET_ADMIN) for administrative commands. Give the TIPCv2 mutators
the equivalent generic-netlink gate. Use GENL_UNS_ADMIN_PERM, which
maps to the same namespace-aware CAP_NET_ADMIN check that
netlink_net_capable() performs, so the behaviour matches the legacy
path and keeps working for CAP_NET_ADMIN holders in a non-initial user
namespace (containers).

A QEMU/KASAN repro run as uid/gid 65534 with zero effective
capabilities previously succeeded in changing the network id and node
identity, setting and flushing key material, and enabling/disabling a
UDP bearer. With this patch applied the same operations fail with
-EPERM.

## References
- https://git.kernel.org/stable/c/52864c6c13dcc292481eabfeb3c31a86c3ec06f2
- https://git.kernel.org/stable/c/56f0a2e0a1d004e025cd031c3a801ab73959269f
- https://git.kernel.org/stable/c/86b0c540e2ea397cde021eecd24145f7c16a3d4e
- https://git.kernel.org/stable/c/9b937de4b3ded62a24da6e8d9d623cdb2748fa74
- https://git.kernel.org/stable/c/b06fb5f78a9af0929aaa47c92d0b7bca0617fb25
- https://git.kernel.org/stable/c/c9668a4adb2264625daeeabc7466b783badd4614
- https://git.kernel.org/stable/c/cebaefe1aceb650d5c99a4c0e1a4dde09e211818
- https://git.kernel.org/stable/c/e87dcc1a644d087de0bb6c94c6dd28c29b89597f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74283.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74283
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
