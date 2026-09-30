# [M] CVE-2023-42756

## Summary
Severity: Medium
Advisory: CVE-2023-42756
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-28
Source: https://osv.dev/vulnerability/CVE-2023-42756
Type: osv

## Details
A flaw was found in the Netfilter subsystem of the Linux kernel. A race condition between IPSET_CMD_ADD and IPSET_CMD_SWAP can lead to a kernel panic due to the invocation of `__ip_set_put` on a wrong `set`. This issue may allow a local user to crash the system.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GISYSL3F6WIEVGHJGLC2MFNTUXHPTKQH/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GPMICQ2HVZO5UAM5KPXHAZKA2U3ZDOO6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/V5PDNWPKAP3WL5RQZ4RIDS6MG32OHH5R/
- https://access.redhat.com/errata/RHSA-2024:2394
- https://seclists.org/oss-sec/2023/q3/242
- https://access.redhat.com/security/cve/CVE-2023-42756
- https://bugzilla.redhat.com/show_bug.cgi?id=2239848
