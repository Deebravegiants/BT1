# [H] wifi: mac80211: check/clear fast rx for non-4addr sta VLAN changes

## Summary
Severity: High
Advisory: CVE-2024-35789
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35789
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.12.0 <6.1.84, >=5.16.0 <6.6.24, >=6.2.0 <6.7.12, >=6.7.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: check/clear fast rx for non-4addr sta VLAN changes

When moving a station out of a VLAN and deleting the VLAN afterwards, the
fast_rx entry still holds a pointer to the VLAN's netdev, which can cause
use-after-free bugs. Fix this by immediately calling ieee80211_check_fast_rx
after the VLAN change.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/2884a50f52313a7a911de3afcad065ddbb3d78fc
- https://git.kernel.org/stable/c/4f2bdb3c5e3189297e156b3ff84b140423d64685
- https://git.kernel.org/stable/c/6b948b54c8bd620725e0c906e44b10c0b13087a7
- https://git.kernel.org/stable/c/7eeabcea79b67cc29563e6a9a5c81f9e2c664d5b
- https://git.kernel.org/stable/c/be1dd9254fc115321d6fbee042026d42afc8d931
- https://git.kernel.org/stable/c/c8bddbd91bc8e42c961a5e2cec20ab879f21100f
- https://git.kernel.org/stable/c/e8678551c0243f799b4859448781cbec1bd6f1cb
- https://git.kernel.org/stable/c/e8b067c4058c0121ac8ca71559df8e2e08ff1a7e
- https://git.kernel.org/stable/c/ea9a0cfc07a7d3601cc680718d9cff0d6927a921
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35789.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35789
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
