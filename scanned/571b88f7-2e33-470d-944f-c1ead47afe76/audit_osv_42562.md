# [H] vxlan: require CAP_NET_ADMIN in the device netns for changelink

## Summary
Severity: High
Advisory: CVE-2026-68432
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68432
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: require CAP_NET_ADMIN in the device netns for changelink

A tunnel changelink() operates on at most two netns, dev_net(dev) and
the sticky underlay netns vxlan->net. They differ once the device is
created in or moved to a netns other than the one the request runs in.
The rtnl changelink path checks CAP_NET_ADMIN only against dev_net(dev),
so a caller privileged there but not in vxlan->net can rewrite a vxlan
device whose underlay lives in vxlan->net.

vxlan_changelink() validates and applies the new configuration against
vxlan->net (vxlan_config_validate(vxlan->net, ...)) and can reopen the
underlay socket in that netns, so the same reasoning as the tunnel
changelink series applies here.

Gate vxlan_changelink() with rtnl_dev_link_net_capable(), at the top of
the op before any attribute is parsed, matching ipgre_changelink() and
the rest of the "require CAP_NET_ADMIN in the device netns for
changelink" series.

Found by 0sec automated security-research tooling (https://0sec.ai).

## References
- https://git.kernel.org/stable/c/0aa580a8bbbed2507b4582a1f0ef581d480d06ed
- https://git.kernel.org/stable/c/32d10c46bfde3e9b274e9e1bd6399d0ebea8f60f
- https://git.kernel.org/stable/c/3a61bd9637f3d929aa846e4eb3d98b48c26fcb0e
- https://git.kernel.org/stable/c/730c7e5fea7f06e0cdf21c547222ec93234fd1d6
- https://git.kernel.org/stable/c/7465ade989ba84adc2bfa58bad3ca25d249f0f7a
- https://git.kernel.org/stable/c/b3793d7dccb192ffff29894d11824db6251acdd5
- https://git.kernel.org/stable/c/b95a8743e58f7efed5ddc4cb73829b66f17feab0
- https://git.kernel.org/stable/c/e8ad0d311e225939a9a6c745d6cc384c7364ec87
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68432.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68432
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
