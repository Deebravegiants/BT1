# [C] Libxml: type confusion leads to denial of service (dos)

## Summary
Severity: Critical
Advisory: CVE-2025-49796
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-49796
Type: osv

## Details
A vulnerability was found in libxml2. Processing certain sch:name elements from the input XML file can trigger a memory corruption issue. This flaw allows an attacker to craft a malicious XML input file that can lead libxml to crash, resulting in a denial of service or other possible undefined behavior due to sensitive data being corrupted in memory.

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
- https://access.redhat.com/errata/RHSA-2025:13267
- https://access.redhat.com/errata/RHSA-2025:13335
- https://access.redhat.com/errata/RHSA-2025:15397
- https://access.redhat.com/errata/RHSA-2025:15827
