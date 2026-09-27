# [H] Libsoup: null pointer dereference in  soup_message_headers_get_content_disposition when "filename" parameter  is present, but has no value in content-disposition header

## Summary
Severity: High
Advisory: CVE-2025-32913
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/CVE-2025-32913
Type: osv

## Details
A flaw was found in libsoup, where the soup_message_headers_get_content_disposition() function is vulnerable to a NULL pointer dereference. This flaw allows a malicious HTTP peer to crash a libsoup client or server that uses this function.

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
- https://access.redhat.com/errata/RHSA-2025:8292
- https://access.redhat.com/errata/RHSA-2025:9179
- https://access.redhat.com/security/cve/CVE-2025-32913
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32913.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32913
- https://bugzilla.redhat.com/show_bug.cgi?id=2359357
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/435
- https://gitlab.gnome.org/GNOME/libsoup/
