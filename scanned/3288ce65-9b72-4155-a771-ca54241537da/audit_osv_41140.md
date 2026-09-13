# [H] Glib: off-by-one error in glib/gkeyfile.c via "g_key_file_get_locale_string_list"

## Summary
Severity: High
Advisory: CVE-2026-58014
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58014
Type: osv

## Details
A flaw was found in GLib. An off-by-one error can occur in the g_key_file_get_locale_string_list function in the gkeyfile.c file when loading a key file with an empty value. This flaw can cause an out-of-bounds access of 1 byte or a denial of service when the out-of-bounds access crosses a page boundary.

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
