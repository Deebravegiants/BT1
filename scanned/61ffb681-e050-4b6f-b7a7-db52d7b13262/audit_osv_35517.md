# [M] Libxml2: libxml2: denial of service via uncontrolled recursion in xml catalog processing

## Summary
Severity: Medium
Advisory: CVE-2026-0990
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2026-0990
Type: osv

## Details
A flaw was found in libxml2, an XML parsing library. This uncontrolled recursion vulnerability occurs in the xmlCatalogXMLResolveURI function when an XML catalog contains a delegate URI entry that references itself. A remote attacker could exploit this configuration-dependent issue by providing a specially crafted XML catalog, leading to infinite recursion and call stack exhaustion. This ultimately results in a segmentation fault, causing a Denial of Service (DoS) by crashing affected applications.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/jbossnetwork/restricted/listSoftware.html
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:7519
- https://access.redhat.com/security/cve/CVE-2026-0990
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0990.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0990
- https://bugzilla.redhat.com/show_bug.cgi?id=2429959
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/1018
