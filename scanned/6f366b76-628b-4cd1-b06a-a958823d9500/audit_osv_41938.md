# [C] net: bcmgenet: keep RBUF EEE/PM disabled

## Summary
Severity: Critical
Advisory: CVE-2026-64125
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64125
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: bcmgenet: keep RBUF EEE/PM disabled

Setting RBUF_EEE_EN | RBUF_PM_EN in RBUF_ENERGY_CTRL breaks the RX
path on GENET hardware once MAC EEE becomes active. RX traffic stops
flowing while the link stays up and the usual descriptor/RX error
counters remain quiet. In that state the MAC still accepts frames
(rbuf_ovflow_cnt keeps climbing) but RBUF no longer forwards them to
DMA, so rx_packets is no longer incremented at the netdev level. On
some boards the corruption ends up as a paging fault in
skb_release_data via bcmgenet_rx_poll on an LPI exit.

Reproduced on Pi 4B (BCM2711 + BCM54213PE) and confirmed by Florian
Fainelli on an internal Broadcom 4908-family board with the same crash
signature. RBUF_PM_EN is not publicly documented.

This shows up more often now that phy_support_eee() enables EEE by
default, but it also affects older kernels as soon as TX LPI is
turned on via ethtool, so it is not specific to recent changes.

Always clear RBUF_EEE_EN | RBUF_PM_EN in bcmgenet_eee_enable_set so
the bits stay off across resets. UMAC and TBUF setup is left alone so
TX-side EEE keeps working.

## References
- https://git.kernel.org/stable/c/2040eb83f6ada148fb32dd98b943a498005d79f2
- https://git.kernel.org/stable/c/289499907399c5a9f2ed82cb34df49112bb8488f
- https://git.kernel.org/stable/c/3d4ef05266ab16d8ef7dd21658a557801eb78704
- https://git.kernel.org/stable/c/49bdf6bbb21b9c6e3f4d0c1910bf0ef98424be95
- https://git.kernel.org/stable/c/9a1730245e416d11ad5c0f2c100061d61cc43f60
- https://git.kernel.org/stable/c/a212fc08f5c48a16a94092bf0a9a8b7cf4483b11
- https://git.kernel.org/stable/c/b579f3a73da7a7e74213558f4cc3d865c30aaa78
- https://git.kernel.org/stable/c/f2782ddac82c70df313012da5f71f1f06b5553ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64125.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64125
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
