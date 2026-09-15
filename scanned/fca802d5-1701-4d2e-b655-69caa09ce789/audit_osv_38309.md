# [M] Gnutls: gnutls: policy bypass due to case-sensitive nameconstraints comparison

## Summary
Severity: Medium
Advisory: CVE-2026-3833
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-3833
Type: osv

## Details
A flaw was found in gnutls. This vulnerability occurs because gnutls performs case-sensitive comparisons of `nameConstraints` labels, specifically for `dNSName` (DNS) or `rfc822Name` (email) constraints within `excludedSubtrees` or `permittedSubtrees`. A remote attacker can exploit this by crafting a leaf certificate with casing differences in the Subject Alternative Name (SAN), leading to a policy bypass where a certificate that should be rejected is instead accepted. This could result in unauthorized access or information disclosure.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:13274
- https://access.redhat.com/errata/RHSA-2026:20611
- https://access.redhat.com/errata/RHSA-2026:20612
- https://access.redhat.com/errata/RHSA-2026:20613
- https://access.redhat.com/errata/RHSA-2026:26319
- https://access.redhat.com/errata/RHSA-2026:26409
- https://access.redhat.com/errata/RHSA-2026:29197
- https://access.redhat.com/errata/RHSA-2026:30004
- https://access.redhat.com/errata/RHSA-2026:30849
- https://access.redhat.com/errata/RHSA-2026:30850
- https://access.redhat.com/errata/RHSA-2026:32962
- https://access.redhat.com/errata/RHSA-2026:33125
- https://access.redhat.com/errata/RHSA-2026:41921
- https://access.redhat.com/errata/RHSA-2026:43575
- https://access.redhat.com/errata/RHSA-2026:57402
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/errata/RHSA-2026:59831
- https://access.redhat.com/errata/RHSA-2026:60019
