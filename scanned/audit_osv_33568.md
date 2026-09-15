# [M] Libsoup: memory leak on soup_header_parse_quality_list() via soup-headers.c

## Summary
Severity: Medium
Advisory: CVE-2025-46420
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-04-24
Source: https://osv.dev/vulnerability/CVE-2025-46420
Type: osv

## Details
A flaw was found in libsoup. It is vulnerable to memory leaks in the soup_header_parse_quality_list() function when parsing a quality list that contains elements with all zeroes.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:4439
- https://access.redhat.com/errata/RHSA-2025:4440
- https://access.redhat.com/errata/RHSA-2025:4508
- https://access.redhat.com/errata/RHSA-2025:4538
- https://access.redhat.com/errata/RHSA-2025:4560
- https://access.redhat.com/errata/RHSA-2025:4568
- https://access.redhat.com/errata/RHSA-2025:4609
- https://access.redhat.com/errata/RHSA-2025:4624
- https://access.redhat.com/errata/RHSA-2025:7436
- https://access.redhat.com/security/cve/CVE-2025-46420
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46420.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-46420
- https://bugzilla.redhat.com/show_bug.cgi?id=2361963
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/438
- https://gitlab.gnome.org/GNOME/libsoup
