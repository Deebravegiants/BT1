# [M] Glib: buffer over-read in glib/gvariant-serialiser.c via gvs_tuple_is_normal()

## Summary
Severity: Medium
Advisory: CVE-2026-58010
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58010
Type: osv

## Details
A flaw was found in GLib. An off-by-one error can occur in the gvs_tuple_is_normal function in the glib/gvariant-serialiser.c file when doing an alignment padding check because the bounds check uses > instead of >=, causing an out-of-bounds read of only 1 byte. This issue can cause a minor information disclosure of 1 byte and a denial of service when the out-of-bounds read crosses a page boundary.

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
