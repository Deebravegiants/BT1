# [C] Libxml: heap use after free (uaf) leads to denial of service (dos)

## Summary
Severity: Critical
Advisory: CVE-2025-49794
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-49794
Type: osv

## Details
A use-after-free vulnerability was found in libxml2. This issue occurs when parsing XPath elements under certain circumstances when the XML schematron has the <sch:name path="..."/> schema elements. This flaw allows a malicious actor to craft a malicious XML document used as input for libxml, resulting in the program's crash using libxml or other possible undefined behaviors.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/07/msg00014.html
- https://access.redhat.com/errata/RHSA-2025:10630
- https://access.redhat.com/errata/RHSA-2025:10698
- https://access.redhat.com/errata/RHSA-2025:10699
- https://access.redhat.com/errata/RHSA-2025:11580
- https://access.redhat.com/errata/RHSA-2025:12098
- https://access.redhat.com/errata/RHSA-2025:12099
- https://access.redhat.com/errata/RHSA-2025:12199
- https://access.redhat.com/errata/RHSA-2025:12237
- https://access.redhat.com/errata/RHSA-2025:12239
- https://access.redhat.com/errata/RHSA-2025:12240
- https://access.redhat.com/errata/RHSA-2025:12241
- https://access.redhat.com/errata/RHSA-2025:13335
- https://access.redhat.com/errata/RHSA-2025:15397
- https://access.redhat.com/errata/RHSA-2025:15827
- https://access.redhat.com/errata/RHSA-2025:15828
