# [H] eth: bnxt: always recalculate features after XDP clearing, fix null-deref

## Summary
Severity: High
Advisory: CVE-2025-21682
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21682
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

eth: bnxt: always recalculate features after XDP clearing, fix null-deref

Recalculate features when XDP is detached.

Before:
  # ip li set dev eth0 xdp obj xdp_dummy.bpf.o sec xdp
  # ip li set dev eth0 xdp off
  # ethtool -k eth0 | grep gro
  rx-gro-hw: off [requested on]

After:
  # ip li set dev eth0 xdp obj xdp_dummy.bpf.o sec xdp
  # ip li set dev eth0 xdp off
  # ethtool -k eth0 | grep gro
  rx-gro-hw: on

The fact that HW-GRO doesn't get re-enabled automatically is just
a minor annoyance. The real issue is that the features will randomly
come back during another reconfiguration which just happens to invoke
netdev_update_features(). The driver doesn't handle reconfiguring
two things at a time very robustly.

Starting with commit 98ba1d931f61 ("bnxt_en: Fix RSS logic in
__bnxt_reserve_rings()") we only reconfigure the RSS hash table
if the "effective" number of Rx rings has changed. If HW-GRO is
enabled "effective" number of rings is 2x what user sees.
So if we are in the bad state, with HW-GRO re-enablement "pending"
after XDP off, and we lower the rings by / 2 - the HW-GRO rings
doing 2x and the ethtool -L doing / 2 may cancel each other out,
and the:

  if (old_rx_rings != bp->hw_resc.resv_rx_rings &&

condition in __bnxt_reserve_rings() will be false.
The RSS map won't get updated, and we'll crash with:

  BUG: kernel NULL pointer dereference, address: 0000000000000168
  RIP: 0010:__bnxt_hwrm_vnic_set_rss+0x13a/0x1a0
    bnxt_hwrm_vnic_rss_cfg_p5+0x47/0x180
    __bnxt_setup_vnic_p5+0x58/0x110
    bnxt_init_nic+0xb72/0xf50
    __bnxt_open_nic+0x40d/0xab0
    bnxt_open_nic+0x2b/0x60
    ethtool_set_channels+0x18c/0x1d0

As we try to access a freed ring.

The issue is present since XDP support was added, really, but
prior to commit 98ba1d931f61 ("bnxt_en: Fix RSS logic in
__bnxt_reserve_rings()") it wasn't causing major issues.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/076a694a42ae3f0466bc6e4126050eeb7b7d299a
- https://git.kernel.org/stable/c/08831a894d18abfaabb5bbde7c2069a7fb41dd93
- https://git.kernel.org/stable/c/90336fc3d6f5e716ac39a9ddbbde453e23a5aa65
- https://git.kernel.org/stable/c/f0aa6a37a3dbb40b272df5fc6db93c114688adcd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21682.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21682
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
