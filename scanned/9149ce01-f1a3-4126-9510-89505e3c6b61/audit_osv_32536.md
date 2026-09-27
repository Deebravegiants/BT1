# [M] Libsoup: heap buffer overflows in sniff_feed_or_html() and skip_insignificant_space()

## Summary
Severity: Medium
Advisory: CVE-2025-32053
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-32053
Type: osv

## Details
A flaw was found in libsoup. A vulnerability in sniff_feed_or_html() and skip_insignificant_space() functions may lead to a heap buffer over-read.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00036.html
- https://access.redhat.com/errata/RHSA-2025:4440
- https://access.redhat.com/errata/RHSA-2025:4508
- https://access.redhat.com/errata/RHSA-2025:4560
- https://access.redhat.com/errata/RHSA-2025:4568
- https://access.redhat.com/errata/RHSA-2025:7436
- https://access.redhat.com/errata/RHSA-2025:8292
- https://access.redhat.com/security/cve/CVE-2025-32053
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32053.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32053
- https://bugzilla.redhat.com/show_bug.cgi?id=2357070
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/426
- https://gitlab.gnome.org/GNOME/libsoup/
