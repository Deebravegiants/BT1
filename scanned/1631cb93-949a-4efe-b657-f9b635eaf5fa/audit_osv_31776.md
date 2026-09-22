# [H] openvswitch: use RCU protection in ovs_vport_cmd_fill_info()

## Summary
Severity: High
Advisory: CVE-2025-21761
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21761
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

openvswitch: use RCU protection in ovs_vport_cmd_fill_info()

ovs_vport_cmd_fill_info() can be called without RTNL or RCU.

Use RCU protection and dev_net_rcu() to avoid potential UAF.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/5828937742af74666192835d657095d95c53dbd0
- https://git.kernel.org/stable/c/7e01abc34e87abd091e619161a20f54ed4e3e2da
- https://git.kernel.org/stable/c/8ec57509c36c8b9a23e50b7858dda0c520a2d074
- https://git.kernel.org/stable/c/90b2f49a502fa71090d9f4fe29a2f51fe5dff76d
- https://git.kernel.org/stable/c/a849a10de5e04d798f7f286a2f1ca174719a617a
- https://git.kernel.org/stable/c/a8816b3f1f151373fd30f1996f00480126c8bb11
- https://git.kernel.org/stable/c/a884f57600e463f69d7b279c4598b865260b62a1
- https://git.kernel.org/stable/c/e85a25d1a9985645e796039e843d1de581d2de1e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21761.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21761
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
