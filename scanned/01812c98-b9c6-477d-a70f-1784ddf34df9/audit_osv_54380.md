# [M] CVE-2023-5380

## Summary
Severity: Medium
Advisory: CVE-2023-5380
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-5380
Type: osv

## Details
A use-after-free flaw was found in the xorg-x11-server. An X server crash may occur in a very specific and legacy configuration (a multi-screen setup with multiple protocol screens, also known as Zaphod mode) if the pointer is warped from within a window on one screen to the root window of the other screen and if the original window is destroyed followed by another window being destroyed.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3RK66CXMXO3PCPDU3GDY5FK4UYHUXQJT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AKKIE626TZOOPD533EYN47J4RFNHZVOP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2WS5E7H4A5J3U5YBCTMRPQVGWK5LVH7D/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HO2Q2NP6R62ZRQQG3XQ4AXUT7J2EKKKY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TJXNI4BXURC2BKPNAHFJK3C5ZETB7PER/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SN6KV4XGQJRVAOSM5C3CWMVAXO53COIP/
- https://security.netapp.com/advisory/ntap-20231130-0004/
- https://access.redhat.com/errata/RHSA-2024:2169
- https://access.redhat.com/errata/RHSA-2024:2298
- https://access.redhat.com/security/cve/CVE-2023-5380
- https://www.debian.org/security/2023/dsa-5534
- https://access.redhat.com/errata/RHSA-2023:7428
- https://access.redhat.com/errata/RHSA-2024:2995
- https://access.redhat.com/errata/RHSA-2024:3067
- https://security.gentoo.org/glsa/202401-30
- https://bugzilla.redhat.com/show_bug.cgi?id=2244736
- https://lists.x.org/archives/xorg-announce/2023-October/003430.html
