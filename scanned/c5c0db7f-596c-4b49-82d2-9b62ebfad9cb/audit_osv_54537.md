# [H] CVE-2024-0841

## Summary
Severity: High
Advisory: CVE-2024-0841
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-28
Source: https://osv.dev/vulnerability/CVE-2024-0841
Type: osv

## Details
A null pointer dereference flaw was found in the hugetlbfs_fill_super function in the Linux kernel hugetlbfs (HugeTLB pages) functionality. This issue may allow a local user to crash the system or potentially escalate their privileges on the system.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://access.redhat.com/errata/RHSA-2024:2394
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2024-0841
- https://bugzilla.redhat.com/show_bug.cgi?id=2256490
