# [H]  Infinispan REST Server's cache retrieval endpoints do not properly evaluate the necessary admin permissions

## Summary
Severity: High
Advisory: GHSA-r4w2-hjmr-36m7
CVE: CVE-2023-3629
CWE: CWE-304
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-30
Source: https://github.com/advisories/GHSA-r4w2-hjmr-36m7
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-server-rest` — affected >=15.0.0.Dev01 <15.0.0.Dev04
- Maven: `org.infinispan:infinispan-server-rest` — affected >=0 <14.0.18.Final

## Details
A flaw was found in Infinispan's REST, Cache retrieval endpoints do not properly evaluate the necessary admin permissions for the operation. This issue could allow an authenticated user to access information outside of their intended permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3629
- https://github.com/infinispan/infinispan/commit/11b3cb0f7ba68b73dd32f655ff3f3df842a0c6bd
- https://github.com/infinispan/infinispan/commit/1e3cc542336d2f49743ab8176ed6f1175e034c59
- https://access.redhat.com/errata/RHSA-2023:5396
- https://access.redhat.com/security/cve/CVE-2023-3629
- https://bugzilla.redhat.com/show_bug.cgi?id=2217926
- https://github.com/infinispan/infinispan
- https://security.netapp.com/advisory/ntap-20240125-0004
