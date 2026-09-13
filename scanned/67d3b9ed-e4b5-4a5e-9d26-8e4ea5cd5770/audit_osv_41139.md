# [M] Glib: buffer over-read in glib/giochannel.c via "g_io_channel_read_line_backend"

## Summary
Severity: Medium
Advisory: CVE-2026-58013
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58013
Type: osv

## Details
A flaw was found in GLib. A buffer over-read can occur in g_io_channel_read_line_backend() in the giochannel.c file when a custom line terminator with a length greater than one is set, causing memcmp to read past the GString buffer. This vulnerability can cause a minor information disclosure of 7 bytes or a denial of service when the buffer over-read crosses a page boundary.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:49512
- https://access.redhat.com/errata/RHSA-2026:55440
- https://access.redhat.com/errata/RHSA-2026:57015
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/errata/RHSA-2026:61766
- https://access.redhat.com/errata/RHSA-2026:61783
- https://access.redhat.com/errata/RHSA-2026:63135
- https://access.redhat.com/errata/RHSA-2026:63138
- https://access.redhat.com/errata/RHSA-2026:63140
- https://access.redhat.com/errata/RHSA-2026:65762
- https://access.redhat.com/errata/RHSA-2026:65763
- https://access.redhat.com/errata/RHSA-2026:65767
- https://access.redhat.com/errata/RHSA-2026:65768
- https://access.redhat.com/errata/RHSA-2026:65769
- https://access.redhat.com/errata/RHSA-2026:65770
- https://access.redhat.com/errata/RHSA-2026:65771
- https://access.redhat.com/errata/RHSA-2026:65773
- https://access.redhat.com/errata/RHSA-2026:66018
