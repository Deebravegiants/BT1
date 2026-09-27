# [M] Libsoup: integer overflow in append_param_quoted

## Summary
Severity: Medium
Advisory: CVE-2025-32050
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-32050
Type: osv

## Details
A flaw was found in libsoup. The libsoup append_param_quoted() function may contain an overflow bug resulting in a buffer under-read.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00036.html
- https://access.redhat.com/errata/RHSA-2025:4440
- https://access.redhat.com/errata/RHSA-2025:4508
- https://access.redhat.com/errata/RHSA-2025:4560
- https://access.redhat.com/errata/RHSA-2025:4568
- https://access.redhat.com/errata/RHSA-2025:7436
- https://access.redhat.com/errata/RHSA-2025:8292
- https://access.redhat.com/security/cve/CVE-2025-32050
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32050.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32050
- https://bugzilla.redhat.com/show_bug.cgi?id=2357067
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/424
- https://gitlab.gnome.org/GNOME/libsoup/
