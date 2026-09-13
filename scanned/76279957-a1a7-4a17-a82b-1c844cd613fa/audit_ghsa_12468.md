# [H] Infinispan circular object references causes out of memory errors

## Summary
Severity: High
Advisory: GHSA-488m-w9fp-5mm2
CVE: CVE-2023-5236
CWE: CWE-1047
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-28
Source: https://github.com/advisories/GHSA-488m-w9fp-5mm2
Type: github-advisory

## Affected
- Maven: `org.infinispan.protostream:protostream` — affected >=0 <4.6.2.Final

## Details
A flaw was found in Infinispan, which does not detect circular object references when unmarshalling. An authenticated attacker with sufficient permissions could insert a maliciously constructed object into the cache and use it to cause out of memory errors and achieve a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5236
- https://github.com/infinispan/protostream/commit/4501b6b307a6bab545346f66238f8be7e42f83eb
- https://github.com/infinispan/protostream/commit/4ef66958f2c4890ae1c6a7acd629d27bd88aa4cb
- https://github.com/infinispan/protostream/commit/50320b5987dc87bc04b616b87e8cf93472ee19c1
- https://access.redhat.com/errata/RHSA-2023:5396
- https://access.redhat.com/security/cve/CVE-2023-5236
- https://bugzilla.redhat.com/show_bug.cgi?id=2240999
- https://github.com/infinispan/infinispan
- https://issues.redhat.com/browse/IPROTO-262
- https://issues.redhat.com/browse/IPROTO-263
- https://issues.redhat.com/browse/ISPN-14534
- https://security.netapp.com/advisory/ntap-20240125-0004
