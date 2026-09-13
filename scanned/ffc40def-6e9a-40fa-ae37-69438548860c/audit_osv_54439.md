# [H] CVE-2023-6270

## Summary
Severity: High
Advisory: CVE-2023-6270
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-04
Source: https://osv.dev/vulnerability/CVE-2023-6270
Type: osv

## Details
A flaw was found in the ATA over Ethernet (AoE) driver in the Linux kernel. The aoecmd_cfg_pkts() function improperly updates the refcnt on `struct net_device`, and a use-after-free can be triggered by racing between the free on the struct and the access through the `skbtxq` global queue. This could lead to a denial of service condition or potential code execution.

## References
- https://access.redhat.com/security/cve/CVE-2023-6270
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2256786
