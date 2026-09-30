# [M] A flaw was found in glib

## Summary
Severity: Medium
Advisory: JLSEC-2026-489
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-489
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.86.3+0

## Details
A flaw was found in glib. This vulnerability allows a heap buffer overflow and denial-of-service (DoS) via an integer overflow in GLib's GIO (GLib Input/Output) `escape_byte_string()` function when processing malicious file or remote filesystem attribute values.

## References
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
- https://access.redhat.com/errata/RHSA-2026:7461
- https://access.redhat.com/security/cve/CVE-2025-14512
- https://bugzilla.redhat.com/show_bug.cgi?id=2421339
