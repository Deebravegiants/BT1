# [M]  CoreDNS may return invalid cache entries

## Summary
Severity: Medium
Advisory: GHSA-m9w6-wp3h-vq8g
CVE: CVE-2024-0874
CWE: CWE-524
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-04-25
Source: https://github.com/advisories/GHSA-m9w6-wp3h-vq8g
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.11.2

## Details
A flaw was found in coredns. This issue could lead to invalid cache entries returning due to incorrectly implemented caching.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-0874
- https://github.com/coredns/coredns/issues/6186
- https://github.com/coredns/coredns/pull/6354
- https://github.com/coredns/coredns/commit/997c7f953962d47c242273f0e41398fdfb5b0151
- https://access.redhat.com/errata/RHSA-2024:0041
- https://access.redhat.com/errata/RHSA-2024:4850
- https://access.redhat.com/errata/RHSA-2024:6009
- https://access.redhat.com/errata/RHSA-2024:6406
- https://access.redhat.com/security/cve/CVE-2024-0874
- https://bugzilla.redhat.com/show_bug.cgi?id=2219234
- https://github.com/coredns/coredns
