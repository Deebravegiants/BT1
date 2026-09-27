# [H] Libsoup: integer underflow in soup_multipart_new_from_message() leading to denial of service in libsoup

## Summary
Severity: High
Advisory: CVE-2025-4948
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-19
Source: https://osv.dev/vulnerability/CVE-2025-4948
Type: osv

## Details
A flaw was found in the soup_multipart_new_from_message() function of the libsoup HTTP library, which is commonly used by GNOME and other applications to handle web communications. The issue occurs when the library processes specially crafted multipart messages. Due to improper validation, an internal calculation can go wrong, leading to an integer underflow. This can cause the program to access invalid memory and crash. As a result, any application or server using libsoup could be forced to exit unexpectedly, creating a denial-of-service (DoS) risk.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:21657
- https://access.redhat.com/errata/RHSA-2025:8126
- https://access.redhat.com/errata/RHSA-2025:8128
- https://access.redhat.com/errata/RHSA-2025:8132
- https://access.redhat.com/errata/RHSA-2025:8139
- https://access.redhat.com/errata/RHSA-2025:8140
- https://access.redhat.com/errata/RHSA-2025:8252
- https://access.redhat.com/errata/RHSA-2025:8480
- https://access.redhat.com/errata/RHSA-2025:8481
- https://access.redhat.com/errata/RHSA-2025:8482
- https://access.redhat.com/errata/RHSA-2025:8663
- https://access.redhat.com/errata/RHSA-2025:9179
- https://access.redhat.com/security/cve/CVE-2025-4948
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4948.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4948
- https://bugzilla.redhat.com/show_bug.cgi?id=2367183
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/449
- https://gitlab.gnome.org/GNOME/libsoup
- https://gitlab.gnome.org/GNOME/libsoup/-/work_items/449
