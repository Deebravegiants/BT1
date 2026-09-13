# [H] Xorg-x11-server: out-of-bounds memory reads/writes in xkb button actions

## Summary
Severity: High
Advisory: CVE-2023-6377
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-6377
Type: osv

## Details
A flaw was found in xorg-server. Querying or changing XKB button actions such as moving from a touchpad to a mouse can result in out-of-bounds memory reads and writes. This may allow local privilege escalation or possible remote code execution in cases where X11 forwarding is involved.

## References
- http://www.openwall.com/lists/oss-security/2023/12/13/1
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/12/msg00008.html
- https://lists.debian.org/debian-lts-announce/2023/12/msg00013.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6R63Z6GIWM3YUNZRCGFODUXLW3GY2HD6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7PP47YXKM5ETLCYEF6473R3VFCJ6QT2S/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IFHV5KCQ2SVOD4QMCPZ5HC6YL44L7YJD/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LJDFWDB7EQVZA45XDP7L5WRSRWS6RVRR/
- https://lists.x.org/archives/xorg-announce/2023-December/003435.html
- https://access.redhat.com/errata/RHSA-2023:7886
- https://access.redhat.com/errata/RHSA-2024:0006
- https://access.redhat.com/errata/RHSA-2024:0009
- https://access.redhat.com/errata/RHSA-2024:0010
- https://access.redhat.com/errata/RHSA-2024:0014
- https://access.redhat.com/errata/RHSA-2024:0015
- https://access.redhat.com/errata/RHSA-2024:0016
- https://access.redhat.com/errata/RHSA-2024:0017
- https://access.redhat.com/errata/RHSA-2024:0018
- https://access.redhat.com/errata/RHSA-2024:0020
- https://access.redhat.com/errata/RHSA-2024:2169
