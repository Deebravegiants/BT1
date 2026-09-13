# [M] Libtasn1: inefficient der decoding in libtasn1 leading to potential remote dos

## Summary
Severity: Medium
Advisory: CVE-2024-12133
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-02-10
Source: https://osv.dev/vulnerability/CVE-2024-12133
Type: osv

## Details
A flaw in libtasn1 causes inefficient handling of specific certificate data. When processing a large number of elements in a certificate, libtasn1 takes much longer than expected, which can slow down or even crash the system. This flaw allows an attacker to send a specially crafted certificate, causing a denial of service attack.

## References
- http://www.openwall.com/lists/oss-security/2025/02/06/6
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://cert-portal.siemens.com/productcert/html/ssa-202008.html
- https://gitlab.com/gnutls/libtasn1/-/blob/master/doc/security/CVE-2024-12133.md
- https://lists.debian.org/debian-lts-announce/2025/02/msg00025.html
- https://access.redhat.com/errata/RHSA-2025:17347
- https://access.redhat.com/errata/RHSA-2025:4049
- https://access.redhat.com/errata/RHSA-2025:7077
- https://access.redhat.com/errata/RHSA-2025:8021
- https://access.redhat.com/errata/RHSA-2025:8385
- https://access.redhat.com/errata/RHSA-2026:30849
- https://access.redhat.com/errata/RHSA-2026:30850
- https://access.redhat.com/errata/RHSA-2026:33125
- https://access.redhat.com/security/cve/CVE-2024-12133
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12133.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12133
- https://security.netapp.com/advisory/ntap-20250523-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2344611
