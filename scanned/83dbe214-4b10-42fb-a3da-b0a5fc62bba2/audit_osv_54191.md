# [M] CVE-2023-42754

## Summary
Severity: Medium
Advisory: CVE-2023-42754
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-05
Source: https://osv.dev/vulnerability/CVE-2023-42754
Type: osv

## Details
A NULL pointer dereference flaw was found in the Linux kernel ipv4 stack. The socket buffer (skb) was assumed to be associated with a device before calling __ip_options_compile, which is not always the case if the skb is re-routed by ipvs. This issue may allow a local user with CAP_NET_ADMIN privileges to crash the system.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GISYSL3F6WIEVGHJGLC2MFNTUXHPTKQH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GPMICQ2HVZO5UAM5KPXHAZKA2U3ZDOO6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/V5PDNWPKAP3WL5RQZ4RIDS6MG32OHH5R/
- https://access.redhat.com/errata/RHSA-2024:2394
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-42754
- https://bugzilla.redhat.com/show_bug.cgi?id=2239845
- https://seclists.org/oss-sec/2023/q4/14
