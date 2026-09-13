# [M] Glib: buffer underflow on glib through glib/gstring.c via function g_string_insert_unichar

## Summary
Severity: Medium
Advisory: CVE-2025-4373
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-05-06
Source: https://osv.dev/vulnerability/CVE-2025-4373
Type: osv

## Details
A flaw was found in GLib, which is vulnerable to an integer overflow in the g_string_insert_unichar() function. When the position at which to insert the character is large, the position will overflow, leading to a buffer underwrite.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://access.redhat.com/errata/RHSA-2025:10855
- https://access.redhat.com/errata/RHSA-2025:11140
- https://access.redhat.com/errata/RHSA-2025:11327
- https://access.redhat.com/errata/RHSA-2025:11373
- https://access.redhat.com/errata/RHSA-2025:11374
- https://access.redhat.com/errata/RHSA-2025:11662
- https://access.redhat.com/errata/RHSA-2025:12275
- https://access.redhat.com/errata/RHSA-2025:13335
- https://access.redhat.com/errata/RHSA-2025:14988
- https://access.redhat.com/errata/RHSA-2025:14989
- https://access.redhat.com/errata/RHSA-2025:14990
- https://access.redhat.com/errata/RHSA-2025:14991
- https://access.redhat.com/security/cve/CVE-2025-4373
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4373.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4373
- https://bugzilla.redhat.com/show_bug.cgi?id=2364265
