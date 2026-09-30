# [H] Infinispan REST Server's bulk read endpoints do not properly evaluate user permissions

## Summary
Severity: High
Advisory: GHSA-fhr7-8jx4-r9cp
CVE: CVE-2023-3628
CWE: CWE-304
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-30
Source: https://github.com/advisories/GHSA-fhr7-8jx4-r9cp
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-server-rest` — affected >=15.0.0.Dev01 <15.0.0.Dev04
- Maven: `org.infinispan:infinispan-server-rest` — affected >=0 <14.0.18.Final

## Details
A flaw was found in Infinispan's REST. Bulk read endpoints do not properly evaluate user permissions for the operation. This issue could allow an authenticated user to access information outside of their intended permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3628
- https://github.com/infinispan/infinispan/commit/70a50352d9195753a588d0fba8c2063b99f96263
- https://github.com/infinispan/infinispan/commit/b34488dcab8bdd4258972568b8405ee7111276ec
- https://access.redhat.com/errata/RHSA-2023:5396
- https://access.redhat.com/security/cve/CVE-2023-3628
- https://bugzilla.redhat.com/show_bug.cgi?id=2217924
- https://github.com/infinispan/infinispan
- https://security.netapp.com/advisory/ntap-20240125-0004
