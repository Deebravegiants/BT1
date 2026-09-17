# [M] Glib: buffer over-read in g_regex_replace() via glib/gregex.c:string_append() and g_utf8_next_char()

## Summary
Severity: Medium
Advisory: CVE-2026-58012
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-58012
Type: osv

## Details
A flaw was found in GLib. A buffer over-read can occur in the g_regex_replace function when used with the `G_REGEX_RAW` compile flag and case-change replacement escapes because the string_append function processes matched substrings using UTF-8 functions that assume valid UTF-8 input, even when the string is treated as raw bytes. This vulnerability can cause a minor information disclosure of 1-5 bytes and a denial of service when the buffer over-read crosses a page boundary.

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
