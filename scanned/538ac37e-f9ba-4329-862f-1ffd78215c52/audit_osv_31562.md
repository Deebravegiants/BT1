# [M] Glib: integer overflow in glib gio attribute escaping causes heap buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2025-14512
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-14512
Type: osv

## Details
A flaw was found in glib. This vulnerability allows a heap buffer overflow and denial-of-service (DoS) via an integer overflow in GLib's GIO (GLib Input/Output) escape_byte_string() function when processing malicious file or remote filesystem attribute values.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:15953
- https://access.redhat.com/errata/RHSA-2026:15969
- https://access.redhat.com/errata/RHSA-2026:15971
- https://access.redhat.com/errata/RHSA-2026:19148
- https://access.redhat.com/errata/RHSA-2026:19361
- https://access.redhat.com/errata/RHSA-2026:19452
- https://access.redhat.com/errata/RHSA-2026:19457
- https://access.redhat.com/errata/RHSA-2026:19459
- https://access.redhat.com/errata/RHSA-2026:19460
- https://access.redhat.com/errata/RHSA-2026:19523
- https://access.redhat.com/errata/RHSA-2026:19524
- https://access.redhat.com/errata/RHSA-2026:19565
- https://access.redhat.com/errata/RHSA-2026:19567
- https://access.redhat.com/errata/RHSA-2026:21275
- https://access.redhat.com/errata/RHSA-2026:22634
- https://access.redhat.com/errata/RHSA-2026:25096
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/errata/RHSA-2026:58981
