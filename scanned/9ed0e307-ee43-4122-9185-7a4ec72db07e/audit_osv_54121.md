# [M] CVE-2023-39198

## Summary
Severity: Medium
Advisory: CVE-2023-39198
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-11-09
Source: https://osv.dev/vulnerability/CVE-2023-39198
Type: osv

## Details
A race condition was found in the QXL driver in the Linux kernel. The qxl_mode_dumb_create() function dereferences the qobj returned by the qxl_gem_object_create_with_handle(), but the handle is the only one holding a reference to it. This flaw allows an attacker to guess the returned handle value and trigger a use-after-free issue, potentially leading to a denial of service or privilege escalation.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://access.redhat.com/errata/RHSA-2024:2394
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-39198
- https://bugzilla.redhat.com/show_bug.cgi?id=2218332
