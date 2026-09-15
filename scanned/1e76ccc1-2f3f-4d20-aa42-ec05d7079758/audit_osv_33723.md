# [M] Xorg-x11-server-xwayland: xorg-x11-server: tigervnc: out-of-bounds read in x rendering extension animated cursors

## Summary
Severity: Medium
Advisory: CVE-2025-49175
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-06-17
Source: https://osv.dev/vulnerability/CVE-2025-49175
Type: osv

## Details
A flaw was found in the X Rendering extension's handling of animated cursors. If a client provides no cursors, the server assumes at least one is present, leading to an out-of-bounds read and potential crash.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/06/msg00028.html
- https://www.x.org/wiki/Development/Security/
- https://access.redhat.com/errata/RHSA-2025:10258
- https://access.redhat.com/errata/RHSA-2025:10342
- https://access.redhat.com/errata/RHSA-2025:10343
- https://access.redhat.com/errata/RHSA-2025:10344
- https://access.redhat.com/errata/RHSA-2025:10346
- https://access.redhat.com/errata/RHSA-2025:10347
- https://access.redhat.com/errata/RHSA-2025:10348
- https://access.redhat.com/errata/RHSA-2025:10349
- https://access.redhat.com/errata/RHSA-2025:10350
- https://access.redhat.com/errata/RHSA-2025:10351
- https://access.redhat.com/errata/RHSA-2025:10352
- https://access.redhat.com/errata/RHSA-2025:10355
- https://access.redhat.com/errata/RHSA-2025:10356
- https://access.redhat.com/errata/RHSA-2025:10360
- https://access.redhat.com/errata/RHSA-2025:10370
- https://access.redhat.com/errata/RHSA-2025:10374
- https://access.redhat.com/errata/RHSA-2025:10375
