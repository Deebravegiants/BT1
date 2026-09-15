# [H] Linux-pam: linux-pam directory traversal

## Summary
Severity: High
Advisory: CVE-2025-6020
Aliases: GHSA-f9p8-gjr4-j9gx
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-17
Source: https://osv.dev/vulnerability/CVE-2025-6020
Type: osv

## Details
A flaw was found in linux-pam. The module pam_namespace may use access user-controlled paths without proper protection, allowing local users to elevate their privileges to root via multiple symlink attacks and race conditions.

## References
- http://www.openwall.com/lists/oss-security/2025/06/17/1
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/09/msg00021.html
- https://access.redhat.com/errata/RHSA-2025:10024
- https://access.redhat.com/errata/RHSA-2025:10027
- https://access.redhat.com/errata/RHSA-2025:10180
- https://access.redhat.com/errata/RHSA-2025:10354
- https://access.redhat.com/errata/RHSA-2025:10357
- https://access.redhat.com/errata/RHSA-2025:10358
- https://access.redhat.com/errata/RHSA-2025:10359
- https://access.redhat.com/errata/RHSA-2025:10361
- https://access.redhat.com/errata/RHSA-2025:10362
- https://access.redhat.com/errata/RHSA-2025:10735
- https://access.redhat.com/errata/RHSA-2025:10823
- https://access.redhat.com/errata/RHSA-2025:11386
- https://access.redhat.com/errata/RHSA-2025:11487
- https://access.redhat.com/errata/RHSA-2025:14557
- https://access.redhat.com/errata/RHSA-2025:15099
