# [M] Libxml2: libxml2: denial of service via crafted xsd-validated document

## Summary
Severity: Medium
Advisory: CVE-2026-6732
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2026-6732
Type: osv

## Details
A flaw was found in libxml2. This vulnerability occurs when the library processes a specially crafted XML Schema Definition (XSD) validated document that includes an internal entity reference. An attacker could exploit this by providing a malicious document, leading to a type confusion error that causes the application to crash. This results in a denial of service (DoS), making the affected system or application unavailable.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/jbossnetwork/restricted/listSoftware.html
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:11503
- https://access.redhat.com/security/cve/CVE-2026-6732
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6732.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6732
- https://bugzilla.redhat.com/show_bug.cgi?id=2461300
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/1097
- https://gitlab.gnome.org/GNOME/libxml2/-/merge_requests/411
