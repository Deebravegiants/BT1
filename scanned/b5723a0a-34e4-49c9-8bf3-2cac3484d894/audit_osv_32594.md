# [H] Libsoup: out of bounds reads in soup_headers_parse_request()

## Summary
Severity: High
Advisory: CVE-2025-32906
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/CVE-2025-32906
Type: osv

## Details
A flaw was found in libsoup, where the soup_headers_parse_request() function may be vulnerable to an out-of-bound read. This flaw allows a malicious user to use a specially crafted HTTP request to crash the HTTP server.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00036.html
- https://access.redhat.com/errata/RHSA-2025:21657
- https://access.redhat.com/errata/RHSA-2025:4439
- https://access.redhat.com/errata/RHSA-2025:4440
- https://access.redhat.com/errata/RHSA-2025:4508
- https://access.redhat.com/errata/RHSA-2025:4538
- https://access.redhat.com/errata/RHSA-2025:4560
- https://access.redhat.com/errata/RHSA-2025:4568
- https://access.redhat.com/errata/RHSA-2025:4609
- https://access.redhat.com/errata/RHSA-2025:4624
- https://access.redhat.com/errata/RHSA-2025:7436
- https://access.redhat.com/errata/RHSA-2025:7505
- https://access.redhat.com/errata/RHSA-2025:8292
- https://access.redhat.com/errata/RHSA-2025:9179
- https://access.redhat.com/security/cve/CVE-2025-32906
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32906.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32906
- https://bugzilla.redhat.com/show_bug.cgi?id=2359341
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/404
