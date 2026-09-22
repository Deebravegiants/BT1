# [H] CVE-2023-42753

## Summary
Severity: High
Advisory: CVE-2023-42753
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-09-25
Source: https://osv.dev/vulnerability/CVE-2023-42753
Type: osv

## Details
An array indexing vulnerability was found in the netfilter subsystem of the Linux kernel. A missing macro could lead to a miscalculation of the `h->nets` array offset, providing attackers with the primitive to arbitrarily increment/decrement a memory buffer out-of-bound. This issue may allow a local user to crash the system or potentially escalate their privileges on the system.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- http://packetstormsecurity.com/files/175963/Kernel-Live-Patch-Security-Notice-LSN-0099-1.html
- https://www.openwall.com/lists/oss-security/2023/09/22/10
- https://access.redhat.com/errata/RHSA-2023:7370
- https://access.redhat.com/errata/RHSA-2024:0376
- https://access.redhat.com/errata/RHSA-2024:0412
- https://access.redhat.com/errata/RHSA-2024:0403
- https://access.redhat.com/errata/RHSA-2024:0562
- https://access.redhat.com/errata/RHSA-2024:0999
- https://access.redhat.com/errata/RHSA-2023:7418
- https://access.redhat.com/errata/RHSA-2023:7539
- https://access.redhat.com/errata/RHSA-2024:0113
- https://access.redhat.com/errata/RHSA-2024:0346
- https://access.redhat.com/errata/RHSA-2023:7379
- https://access.redhat.com/errata/RHSA-2023:7382
- https://access.redhat.com/errata/RHSA-2023:7389
- https://access.redhat.com/errata/RHSA-2023:7411
- https://access.redhat.com/errata/RHSA-2023:7558
- https://access.redhat.com/errata/RHSA-2024:0134
