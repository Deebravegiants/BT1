# [H] geneve: require CAP_NET_ADMIN in the device netns for changelink

## Summary
Severity: High
Advisory: CVE-2026-68142
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68142
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

geneve: require CAP_NET_ADMIN in the device netns for changelink

A tunnel changelink() operates on at most two netns, dev_net(dev) and
the sticky underlay netns geneve->net. They differ once the device is
created in or moved to a netns other than the one the request runs in.
The rtnl changelink path checks CAP_NET_ADMIN only against dev_net(dev),
so a caller privileged there but not in geneve->net can rewrite a geneve
device whose underlay lives in geneve->net.

geneve_changelink() applies the new configuration against geneve->net:
geneve_link_config() and the geneve_quiesce()/geneve_unquiesce() pair
reopen the underlay sockets in that netns (geneve_sock_add() uses
geneve->net), so the same reasoning as the tunnel changelink series
applies here.

Gate geneve_changelink() with rtnl_dev_link_net_capable(), at the top of
the op before any attribute is parsed, matching ipgre_changelink() and
the rest of the "require CAP_NET_ADMIN in the device netns for
changelink" series.

Found by 0sec automated security-research tooling (https://0sec.ai).

## References
- https://git.kernel.org/stable/c/11a7d989d00160481a273eb4f7f05f64b5a6ffdf
- https://git.kernel.org/stable/c/278c6a31ee27c931c722202c8c06cc3253923254
- https://git.kernel.org/stable/c/2abdacc927c92fa6a9cc8341e8c9b88dcb561553
- https://git.kernel.org/stable/c/8efb8f8bbb353b8f2fdf4f37534c6d96c9f69e01
- https://git.kernel.org/stable/c/95f45e20f1b2cec13823f0f68060ab4b2261b2c1
- https://git.kernel.org/stable/c/9de5518fc1fab583526a8f66b8e505c4864dc60a
- https://git.kernel.org/stable/c/a5522963c57f12df5f9db804ebfc472b58eef0ae
- https://git.kernel.org/stable/c/f8c498585d2a08aa623748353c3e61467b7e9fd2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68142.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68142
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
