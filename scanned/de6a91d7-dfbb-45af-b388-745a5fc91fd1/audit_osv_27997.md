# [H] wireguard: netlink: access device through ctx instead of peer

## Summary
Severity: High
Advisory: CVE-2024-26950
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26950
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wireguard: netlink: access device through ctx instead of peer

The previous commit fixed a bug that led to a NULL peer->device being
dereferenced. It's actually easier and faster performance-wise to
instead get the device from ctx->wg. This semantically makes more sense
too, since ctx->wg->peer_allowedips.seq is compared with
ctx->allowedips_seq, basing them both in ctx. This also acts as a
defence in depth provision against freed peers.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/09c3fa70f65175861ca948cb2f0f791e666c90e5
- https://git.kernel.org/stable/c/493aa6bdcffd90a4f82aa614fe4f4db0641b4068
- https://git.kernel.org/stable/c/4be453271a882c8ebc28df3dbf9e4d95e6ac42f5
- https://git.kernel.org/stable/c/71cbd32e3db82ea4a74e3ef9aeeaa6971969c86f
- https://git.kernel.org/stable/c/93bcc1752c69bb309f4d8cfaf960ef1faeb34996
- https://git.kernel.org/stable/c/c991567e6c638079304cc15dff28748e4a3c4a37
- https://git.kernel.org/stable/c/d44bd323d8bb8031eef4bdc44547925998a11e47
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26950.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26950
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
