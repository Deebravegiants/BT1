# [H] CVE-2023-5633

## Summary
Severity: High
Advisory: CVE-2023-5633
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-23
Source: https://osv.dev/vulnerability/CVE-2023-5633
Type: osv

## Details
The reference count changes made as part of the CVE-2023-33951 and CVE-2023-33952 fixes exposed a use-after-free flaw in the way memory objects were handled when they were being used to store a surface. When running inside a VMware guest with 3D acceleration enabled, a local, unprivileged user could potentially use this flaw to escalate their privileges.

## References
- https://access.redhat.com/errata/RHSA-2024:4823
- https://access.redhat.com/errata/RHSA-2024:0113
- https://access.redhat.com/errata/RHSA-2024:0134
- https://access.redhat.com/errata/RHSA-2024:0461
- https://access.redhat.com/errata/RHSA-2024:1404
- https://access.redhat.com/errata/RHSA-2024:4831
- https://access.redhat.com/security/cve/CVE-2023-5633
- https://bugzilla.redhat.com/show_bug.cgi?id=2245663
