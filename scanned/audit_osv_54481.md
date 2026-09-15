# [M] CVE-2023-6915

## Summary
Severity: Medium
Advisory: CVE-2023-6915
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-15
Source: https://osv.dev/vulnerability/CVE-2023-6915
Type: osv

## Details
A Null pointer dereference problem was found in ida_free in lib/idr.c in the Linux Kernel. This issue may allow an attacker using this library to cause a denial of service problem due to a missing check at a function return.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://access.redhat.com/errata/RHSA-2024:2394
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-6915
- https://bugzilla.redhat.com/show_bug.cgi?id=2254982
- https://github.com/torvalds/linux/commit/af73483f4e8b6f5c68c9aa63257bdd929a9c194a
