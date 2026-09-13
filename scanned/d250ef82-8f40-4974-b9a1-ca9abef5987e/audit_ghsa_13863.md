# [C] Undertow client not checking server identity presented by server certificate in https connections

## Summary
Severity: Critical
Advisory: GHSA-pfcc-3g6r-8rg8
CVE: CVE-2022-4492
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-23
Source: https://github.com/advisories/GHSA-pfcc-3g6r-8rg8
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=2.3.0 <2.3.5.Final
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.24.Final

## Details
The undertow client is not checking the server identity presented by the server certificate in https connections. This should be performed by default in https and in http/2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4492
- https://github.com/undertow-io/undertow/pull/1447
- https://github.com/undertow-io/undertow/pull/1447/commits/e5071e52b72529a14d3ec436ae7102cea5d918c4
- https://github.com/undertow-io/undertow/pull/1457
- https://github.com/undertow-io/undertow/pull/1457/commits/a4d3b167126a803cc4f7fb740dd9a6ecabf59342
- https://access.redhat.com/security/cve/CVE-2022-4492
- https://bugzilla.redhat.com/show_bug.cgi?id=2153260
- https://github.com/undertow-io/undertow/blob/master/core/src/main/java/io/undertow/security/impl/ClientCertAuthenticationMechanism.java
- https://issues.redhat.com/browse/MTA-93
- https://issues.redhat.com/browse/UNDERTOW-2212
- https://security.netapp.com/advisory/ntap-20230324-0002
