# [H] Use of Externally-Controlled Input to Select Classes or Code in Infinispan

## Summary
Severity: High
Advisory: GHSA-h47x-2j37-fw5m
CVE: CVE-2019-10174
CWE: CWE-470
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h47x-2j37-fw5m
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-core` — affected >=0 <8.2.12.Final
- Maven: `org.infinispan:infinispan-core` — affected >=9.0.0.Final <9.4.17.Final

## Details
A vulnerability was found in Infinispan such that the invokeAccessibly method from the public class ReflectionUtil allows any application class to invoke private methods in any class with Infinispan's privileges. The attacker can use reflection to introduce new, malicious behavior into the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10174
- https://github.com/infinispan/infinispan/commit/5dbb05cfaca01a1a66732b82a0f5ba615ccbd214
- https://github.com/infinispan/infinispan/commit/7bdc2822ccf79127a488130239c49a5e944e3ca2
- https://access.redhat.com/errata/RHSA-2020:0481
- https://access.redhat.com/errata/RHSA-2020:0727
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10174
- https://github.com/infinispan/infinispan
- https://security.netapp.com/advisory/ntap-20220210-0018
