# [M] CVE-2025-14831

## Summary
Severity: Medium
Advisory: CVE-2025-14831
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2025-14831
Type: osv

## Details
A flaw was found in GnuTLS. This vulnerability allows a denial of service (DoS) by excessive CPU (Central Processing Unit) and memory consumption via specially crafted malicious certificates containing a large number of name constraints and subject alternative names (SANs).

## References
- https://access.redhat.com/security/cve/CVE-2025-14831
- https://access.redhat.com/errata/RHSA-2026:3477
- https://access.redhat.com/errata/RHSA-2026:4188
- https://bugzilla.redhat.com/show_bug.cgi?id=2423177
- https://gitlab.com/gnutls/gnutls/-/issues/1773
