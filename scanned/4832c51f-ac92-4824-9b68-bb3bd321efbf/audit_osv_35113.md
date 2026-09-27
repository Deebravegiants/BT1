# [H] team: Move team device type change at the end of team_port_add

## Summary
Severity: High
Advisory: CVE-2025-68340
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-23
Source: https://osv.dev/vulnerability/CVE-2025-68340
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.10.259, >=5.11.0 <5.15.199, >=5.16.0 <6.1.162, >=6.2.0 <6.6.123, >=6.7.0 <6.12.61, >=6.13.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

team: Move team device type change at the end of team_port_add

Attempting to add a port device that is already up will expectedly fail,
but not before modifying the team device header_ops.

In the case of the syzbot reproducer the gre0 device is
already in state UP when it attempts to add it as a
port device of team0, this fails but before that
header_ops->create of team0 is changed from eth_header to ipgre_header
in the call to team_dev_type_check_change.

Later when we end up in ipgre_header() struct ip_tunnel* points to nonsense
as the private data of the device still holds a struct team.

Example sequence of iproute2 commands to reproduce the hang/BUG():
ip link add dev team0 type team
ip link add dev gre0 type gre
ip link set dev gre0 up
ip link set dev gre0 master team0
ip link set dev team0 up
ping -I team0 1.1.1.1

Move team_dev_type_check_change down where all other checks have passed
as it changes the dev type with no way to restore it in case
one of the checks that follow it fail.

Also make sure to preserve the origial mtu assignment:
  - If port_dev is not the same type as dev, dev takes mtu from port_dev
  - If port_dev is the same type as dev, port_dev takes mtu from dev

This is done by adding a conditional before the call to dev_set_mtu
to prevent it from assigning port_dev->mtu = dev->mtu and instead
letting team_dev_type_check_change assign dev->mtu = port_dev->mtu.
The conditional is needed because the patch moves the call to
team_dev_type_check_change past dev_set_mtu.

Testing:
  - team device driver in-tree selftests
  - Add/remove various devices as slaves of team device
  - syzbot

## References
- https://git.kernel.org/stable/c/0ae9cfc454ea5ead5f3ddbdfe2e70270d8e2c8ef
- https://git.kernel.org/stable/c/4040b5e8963982a00aa821300cb746efc9f2947e
- https://git.kernel.org/stable/c/a74ab1b532ecc5f9106621a8f75b4c3d04466b35
- https://git.kernel.org/stable/c/c8b15b0d2eec3b5c7f585e5a53dfc8d36c818283
- https://git.kernel.org/stable/c/e26235840fd961e4ebe5568f11a2a078cf726663
- https://git.kernel.org/stable/c/e3eed4f038214494af62c7d2d64749e5108ce6ca
- https://git.kernel.org/stable/c/f82d1fb65549de241fe312fcb2bcb8e0ad7b424d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68340.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68340
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
