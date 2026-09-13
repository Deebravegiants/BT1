# [M] CVE-2022-2850

## Summary
Severity: Medium
Advisory: CVE-2022-2850
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/CVE-2022-2850
Type: osv

## Details
A flaw was found In 389-ds-base. When the Content Synchronization plugin is enabled, an authenticated user can reach a NULL pointer dereference using a specially crafted query. This flaw allows an authenticated attacker to cause a denial of service. This CVE is assigned against an incomplete fix of CVE-2021-3514.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00015.html
- https://lists.debian.org/debian-lts-announce/2023/04/msg00026.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2118691
- https://access.redhat.com/security/cve/CVE-2022-2850
