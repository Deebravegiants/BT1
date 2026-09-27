# [H] Libsoup: oob read on libsoup through function  "soup_multipart_new_from_message" in soup-multipart.c leads to crash or  exit of process

## Summary
Severity: High
Advisory: CVE-2025-32914
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-04-14
Source: https://osv.dev/vulnerability/CVE-2025-32914
Type: osv

## Details
A flaw was found in libsoup, where the soup_multipart_new_from_message() function is vulnerable to an out-of-bounds read. This flaw allows a malicious HTTP client to induce the libsoup server to read out of bounds.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00036.html
- https://access.redhat.com/errata/RHSA-2025:21657
- https://access.redhat.com/errata/RHSA-2025:7505
- https://access.redhat.com/errata/RHSA-2025:8126
- https://access.redhat.com/errata/RHSA-2025:8132
- https://access.redhat.com/errata/RHSA-2025:8139
- https://access.redhat.com/errata/RHSA-2025:8140
- https://access.redhat.com/errata/RHSA-2025:8252
- https://access.redhat.com/errata/RHSA-2025:8480
- https://access.redhat.com/errata/RHSA-2025:8481
- https://access.redhat.com/errata/RHSA-2025:8482
- https://access.redhat.com/errata/RHSA-2025:8663
- https://access.redhat.com/errata/RHSA-2025:9179
- https://access.redhat.com/security/cve/CVE-2025-32914
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32914.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32914
- https://bugzilla.redhat.com/show_bug.cgi?id=2359358
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/436
- https://gitlab.gnome.org/GNOME/libsoup/
