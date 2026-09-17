# [M] Infinispan Potential Out of Memory Error via REST Compare API Buffer API

## Summary
Severity: Medium
Advisory: GHSA-2q39-w2hw-2pjm
CVE: CVE-2024-6875
CWE: CWE-401
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-28
Source: https://github.com/advisories/GHSA-2q39-w2hw-2pjm
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-query` — affected 15.1.0.Dev01
- Maven: `org.infinispan:infinispan-query` — affected >=0

## Details
A vulnerability was found in the Infinispan component in Red Hat Data Grid. The REST compare API may have a buffer leak and an out of memory error can occur when sending continual requests with large POST data to the REST API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6875
- https://github.com/infinispan/infinispan/pull/12645
- https://github.com/infinispan/infinispan/pull/12663
- https://access.redhat.com/security/cve/CVE-2024-6875
- https://bugzilla.redhat.com/show_bug.cgi?id=2298555
- https://github.com/infinispan/infinispan
- https://issues.redhat.com/browse/JDG-7169
