# [C] Libsoup: double free on  soup_message_headers_get_content_disposition() through  "soup-message-headers.c" via "params" ghashtable value

## Summary
Severity: Critical
Advisory: CVE-2025-32911
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32911
Type: osv

## Details
A use-after-free type vulnerability was found in libsoup, in the soup_message_headers_get_content_disposition() function. This flaw allows a malicious HTTP client to cause memory corruption in the libsoup server.

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
- https://access.redhat.com/security/cve/CVE-2025-32911
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32911.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32911
- https://bugzilla.redhat.com/show_bug.cgi?id=2359355
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/433
- https://gitlab.gnome.org/GNOME/libsoup/
