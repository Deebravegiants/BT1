# [H] Libxml: null pointer dereference leads to denial of service (dos)

## Summary
Severity: High
Advisory: CVE-2025-49795
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-49795
Type: osv

## Details
A NULL pointer dereference vulnerability was found in libxml2 when processing XPath XML expressions. This flaw allows an attacker to craft a malicious XML input to libxml2, leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://access.redhat.com/errata/RHSA-2025:10630
- https://access.redhat.com/errata/RHSA-2025:19020
- https://access.redhat.com/errata/RHSA-2026:7519
- https://access.redhat.com/security/cve/CVE-2025-49795
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49795.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-49795
- https://bugzilla.redhat.com/show_bug.cgi?id=2372379
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/932
- https://gitlab.gnome.org/GNOME/libxml2/
