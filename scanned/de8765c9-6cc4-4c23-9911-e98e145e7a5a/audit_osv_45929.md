# [C] A flaw was found in GLib (Gnome Lib)

## Summary
Severity: Critical
Advisory: JLSEC-2026-488
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/JLSEC-2026-488
Type: osv

## Affected
- Julia: `Glib_jll` — affected >=0 <2.86.3+0

## Details
A flaw was found in GLib (Gnome Lib). This vulnerability allows a remote attacker to cause heap corruption, leading to a denial of service or potential code execution via a buffer-underflow in the GVariant parser when processing maliciously crafted input strings.

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
- https://access.redhat.com/errata/RHSA-2026:19566
- https://access.redhat.com/errata/RHSA-2026:19567
- https://access.redhat.com/errata/RHSA-2026:21275
- https://access.redhat.com/errata/RHSA-2026:22634
- https://access.redhat.com/errata/RHSA-2026:25096
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/errata/RHSA-2026:7461
- https://access.redhat.com/security/cve/CVE-2025-14087
