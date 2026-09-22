# [H] Libsoup: out-of-bounds read in cookie date handling of libsoup http library

## Summary
Severity: High
Advisory: CVE-2025-11021
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-09-26
Source: https://osv.dev/vulnerability/CVE-2025-11021
Type: osv

## Details
A flaw was found in the cookie date handling logic of the libsoup HTTP library, widely used by GNOME and other applications for web communication. When processing cookies with specially crafted expiration dates, the library may perform an out-of-bounds memory read. This flaw could result in unintended disclosure of memory contents, potentially exposing sensitive information from the process using libsoup.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:18183
- https://access.redhat.com/errata/RHSA-2025:19713
- https://access.redhat.com/errata/RHSA-2025:19714
- https://access.redhat.com/errata/RHSA-2025:20959
- https://access.redhat.com/errata/RHSA-2025:21032
- https://access.redhat.com/errata/RHSA-2025:21655
- https://access.redhat.com/errata/RHSA-2025:21656
- https://access.redhat.com/errata/RHSA-2025:21657
- https://access.redhat.com/errata/RHSA-2025:21664
- https://access.redhat.com/errata/RHSA-2025:21665
- https://access.redhat.com/errata/RHSA-2025:21666
- https://access.redhat.com/errata/RHSA-2025:21772
- https://access.redhat.com/errata/RHSA-2025:22013
- https://access.redhat.com/security/cve/CVE-2025-11021
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11021.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-11021
- https://bugzilla.redhat.com/show_bug.cgi?id=2399627
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/459
- https://gitlab.gnome.org/GNOME/libsoup/
