# [H] CVE-2023-5367

## Summary
Severity: High
Advisory: CVE-2023-5367
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-5367
Type: osv

## Details
A out-of-bounds write flaw was found in the xorg-x11-server. This issue occurs due to an incorrect calculation of a buffer offset when copying data stored in the heap in the XIChangeDeviceProperty function in Xi/xiproperty.c and in RRChangeOutputProperty function in randr/rrproperty.c, allowing for possible escalation of privileges or denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4YBK3I6SETHETBHDETFWM3VSZUQICIDV/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AKKIE626TZOOPD533EYN47J4RFNHZVOP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HO2Q2NP6R62ZRQQG3XQ4AXUT7J2EKKKY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SEDJN4VFN57K5POOC7BNVD6L6WUUCSG6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SN6KV4XGQJRVAOSM5C3CWMVAXO53COIP/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3RK66CXMXO3PCPDU3GDY5FK4UYHUXQJT/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L2RMNR4235YXZZQ2X7Q4MTOZDMZ7BBQU/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2WS5E7H4A5J3U5YBCTMRPQVGWK5LVH7D/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TJXNI4BXURC2BKPNAHFJK3C5ZETB7PER/
- https://access.redhat.com/errata/RHSA-2024:2996
- https://access.redhat.com/errata/RHSA-2024:2169
- https://access.redhat.com/errata/RHSA-2023:6802
- https://access.redhat.com/errata/RHSA-2023:7388
- https://access.redhat.com/errata/RHSA-2023:7405
- https://access.redhat.com/errata/RHSA-2023:7428
- https://access.redhat.com/errata/RHSA-2023:7533
- https://security.gentoo.org/glsa/202401-30
- https://access.redhat.com/errata/RHSA-2023:6808
- https://www.debian.org/security/2023/dsa-5534
