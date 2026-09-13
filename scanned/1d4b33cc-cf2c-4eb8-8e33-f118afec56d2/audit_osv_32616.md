# [M] Gnutls: vulnerability in gnutls othername san export

## Summary
Severity: Medium
Advisory: CVE-2025-32988
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-32988
Type: osv

## Details
A flaw was found in GnuTLS. A double-free vulnerability exists in GnuTLS due to incorrect ownership handling in the export logic of Subject Alternative Name (SAN) entries containing an otherName. If the type-id OID is invalid or malformed, GnuTLS will call asn1_delete_structure() on an ASN.1 node it does not own, leading to a double-free condition when the parent function or caller later attempts to free the same structure.

This vulnerability can be triggered using only public GnuTLS APIs and may result in denial of service or memory corruption, depending on allocator behavior.

## References
- http://www.openwall.com/lists/oss-security/2025/07/11/3
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://lists.debian.org/debian-lts-announce/2025/08/msg00005.html
- https://lists.gnupg.org/pipermail/gnutls-help/2025-July/004883.html
- https://www.gnutls.org/
- https://access.redhat.com/errata/RHSA-2025:16115
- https://access.redhat.com/errata/RHSA-2025:16116
- https://access.redhat.com/errata/RHSA-2025:17181
- https://access.redhat.com/errata/RHSA-2025:17348
- https://access.redhat.com/errata/RHSA-2025:17361
- https://access.redhat.com/errata/RHSA-2025:17415
- https://access.redhat.com/errata/RHSA-2025:19088
- https://access.redhat.com/errata/RHSA-2025:22529
- https://access.redhat.com/errata/RHSA-2026:7477
- https://access.redhat.com/security/cve/CVE-2025-32988
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32988.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32988
- https://bugzilla.redhat.com/show_bug.cgi?id=2359622
