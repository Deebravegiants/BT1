# [M] CVE-2024-0193

## Summary
Severity: Medium
Advisory: CVE-2024-0193
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2024-0193
Type: osv

## Details
A use-after-free flaw was found in the netfilter subsystem of the Linux kernel. If the catchall element is garbage-collected when the pipapo set is removed, the element can be deactivated twice. This can cause a use-after-free issue on an NFT_CHAIN object or NFT_OBJECT object, allowing a local unprivileged user with CAP_NET_ADMIN capability to escalate their privileges on the system.

## References
- https://access.redhat.com/errata/RHSA-2024:1018
- https://access.redhat.com/errata/RHSA-2024:1019
- https://access.redhat.com/errata/RHSA-2024:4415
- https://access.redhat.com/errata/RHSA-2024:1248
- https://access.redhat.com/errata/RHSA-2024:2094
- https://access.redhat.com/errata/RHSA-2024:4412
- https://access.redhat.com/security/cve/CVE-2024-0193
- https://bugzilla.redhat.com/show_bug.cgi?id=2255653
