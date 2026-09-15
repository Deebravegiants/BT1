# [M] Glib: glib: buffer underflow in gvariant parser leads to heap corruption

## Summary
Severity: Medium
Advisory: CVE-2025-14087
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-12-10
Source: https://osv.dev/vulnerability/CVE-2025-14087
Type: osv

## Details
A flaw was found in GLib (Gnome Lib). This vulnerability allows a remote attacker to cause heap corruption, leading to a denial of service or potential code execution via a buffer-underflow in the GVariant parser when processing maliciously crafted input strings.

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
- https://access.redhat.com/errata/RHSA-2026:19566
- https://access.redhat.com/errata/RHSA-2026:19567
- https://access.redhat.com/errata/RHSA-2026:21275
- https://access.redhat.com/errata/RHSA-2026:22634
- https://access.redhat.com/errata/RHSA-2026:25096
- https://access.redhat.com/errata/RHSA-2026:29197
