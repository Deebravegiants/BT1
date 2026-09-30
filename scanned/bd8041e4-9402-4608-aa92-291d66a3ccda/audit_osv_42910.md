# [H] xfrm: xfrm_interface: require CAP_NET_ADMIN in the device netns for changelink

## Summary
Severity: High
Advisory: CVE-2026-72136
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72136
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: xfrm_interface: require CAP_NET_ADMIN in the device netns for changelink

xfrmi_changelink() operates on at most two netns, dev_net(dev) and the
interface link netns xi->net. They differ once the device is created in
or moved to a netns other than the one the request runs in. The rtnl
changelink path checks CAP_NET_ADMIN only against dev_net(dev), so a
caller privileged there but not in xi->net can rewrite an interface that
lives in xi->net.

Gate xfrmi_changelink() on rtnl_dev_link_net_capable() at its top,
before any attribute is parsed.

## References
- https://git.kernel.org/stable/c/04c1aa57d08471b1953bf27c84ac9b3d78d71831
- https://git.kernel.org/stable/c/095515d89b19b6cc19dfcdc846f97403ed1ebce3
- https://git.kernel.org/stable/c/37b61946d278c7deb0d40ba8f2b6fc0478d61dab
- https://git.kernel.org/stable/c/3ba2b2ef7d6a63b190f15cfc2b4ba0fba59928ea
- https://git.kernel.org/stable/c/80ec68bba11f7f387c0e4099c2d7b2c84943eb99
- https://git.kernel.org/stable/c/8ca2a19a987a7d1cb4c916ed9723a1c6993b4276
- https://git.kernel.org/stable/c/bdfd1c21d90e628a58a9de79e024cdfcbedfa15c
- https://git.kernel.org/stable/c/e9c90756f10da334fb31552e52c61f1dba69f491
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72136.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72136
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
