# [H] Undertow denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-m4mm-pg93-fv78
CVE: CVE-2023-1108
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-09-14
Source: https://github.com/advisories/GHSA-m4mm-pg93-fv78
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=2.3.0 <2.3.5.Final
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.24.Final

## Details
A flaw was found in undertow. This issue makes achieving a denial of service possible due to an unexpected handshake status updated in SslConduit, where the loop never terminates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1108
- https://github.com/undertow-io/undertow/pull/1457
- https://github.com/undertow-io/undertow/commit/ccc053b55f5de9872bc1a4999fd6aa85fc5e146d
- https://github.com/undertow-io/undertow/commit/1b763064a41a30583b5df9a118898513007a70be
- https://github.com/undertow-io/undertow/commit/1302c8cf4476936802504efe0d36c58dcd954f78
- https://security.netapp.com/advisory/ntap-20231020-0002
- https://github.com/undertow-io/undertow
- https://github.com/advisories/GHSA-m4mm-pg93-fv78
- https://bugzilla.redhat.com/show_bug.cgi?id=2174246
- https://access.redhat.com/security/cve/CVE-2023-1108
- https://access.redhat.com/errata/RHSA-2023:4612
- https://access.redhat.com/errata/RHSA-2023:3954
- https://access.redhat.com/errata/RHSA-2023:3892
- https://access.redhat.com/errata/RHSA-2023:3888
- https://access.redhat.com/errata/RHSA-2023:3885
- https://access.redhat.com/errata/RHSA-2023:3884
- https://access.redhat.com/errata/RHSA-2023:3883
- https://access.redhat.com/errata/RHSA-2023:2135
- https://access.redhat.com/errata/RHSA-2023:1516
- https://access.redhat.com/errata/RHSA-2023:1514
