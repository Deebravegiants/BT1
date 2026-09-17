# [H] Xorg: xmayland: value overflow in xkbsetcompatmap()

## Summary
Severity: High
Advisory: CVE-2025-62231
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-10-30
Source: https://osv.dev/vulnerability/CVE-2025-62231
Type: osv

## Details
A flaw was identified in the X.Org X server’s X Keyboard (Xkb) extension where improper bounds checking in the XkbSetCompatMap() function can cause an unsigned short overflow. If an attacker sends specially crafted input data, the value calculation may overflow, leading to memory corruption or a crash.

## References
- http://www.openwall.com/lists/oss-security/2025/10/28/7
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/10/msg00033.html
- https://lists.x.org/archives/xorg-announce/2025-October/003635.html
- https://access.redhat.com/errata/RHSA-2025:19432
- https://access.redhat.com/errata/RHSA-2025:19433
- https://access.redhat.com/errata/RHSA-2025:19434
- https://access.redhat.com/errata/RHSA-2025:19435
- https://access.redhat.com/errata/RHSA-2025:19489
- https://access.redhat.com/errata/RHSA-2025:19623
- https://access.redhat.com/errata/RHSA-2025:19909
- https://access.redhat.com/errata/RHSA-2025:20958
- https://access.redhat.com/errata/RHSA-2025:20960
- https://access.redhat.com/errata/RHSA-2025:20961
- https://access.redhat.com/errata/RHSA-2025:21035
- https://access.redhat.com/errata/RHSA-2025:22040
- https://access.redhat.com/errata/RHSA-2025:22041
- https://access.redhat.com/errata/RHSA-2025:22051
- https://access.redhat.com/errata/RHSA-2025:22055
- https://access.redhat.com/errata/RHSA-2025:22056
