# [H] Infinispan: Deserialization of untrusted data in the Hot Rod Java client via automatic byte-array deserialization

## Summary
Severity: High
Advisory: GHSA-4hhg-8ghq-vwq6
CVE: CVE-2016-0750
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4hhg-8ghq-vwq6
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-core` — affected >=0 <9.1.0.Final

## Details
The hotrod java client in infinispan before 9.1.0.Final automatically deserializes bytearray message contents in certain events. A malicious user could exploit this flaw by injecting a specially-crafted serialized object to attain remote code execution or conduct other attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-0750
- https://github.com/infinispan/infinispan/pull/5116
- https://access.redhat.com/errata/RHSA-2017:3244
- https://access.redhat.com/errata/RHSA-2018:0501
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-0750
- https://github.com/infinispan/infinispan
- https://issues.jboss.org/browse/ISPN-7781
- http://www.securityfocus.com/bid/101910
