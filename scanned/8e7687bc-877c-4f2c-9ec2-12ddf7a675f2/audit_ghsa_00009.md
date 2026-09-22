# [M] Moderate severity vulnerability that affects com.fasterxml.jackson.datatype:jackson-datatype-jsr353

## Summary
Severity: Medium
Advisory: GHSA-h4x4-5qp2-wp46
CVE: CVE-2018-1000873
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-12-21
Source: https://github.com/advisories/GHSA-h4x4-5qp2-wp46
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.datatype:jackson-datatype-jsr310` — affected >=0 <2.9.8

## Details
Fasterxml Jackson version Before 2.9.8 contains a CWE-20: Improper Input Validation vulnerability in Jackson-Databind that can result in Causes a denial-of-service (DoS). This attack appear to be exploitable via The victim deserializes malicious input, specifically very large values in the nanoseconds field of a time value. This vulnerability appears to have been fixed in 2.9.8.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000873
- https://github.com/FasterXML/jackson-modules-java8/issues/90
- https://github.com/FasterXML/jackson-modules-java8/pull/87
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://security.netapp.com/advisory/ntap-20200904-0004
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/ff8dcfe29377088ab655fda9d585dccd5b1f07fabd94ae84fd60a7f8@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/bcce5a9c532b386c68dab2f6b3ce8b0cc9b950ec551766e76391caa3@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://github.com/advisories/GHSA-h4x4-5qp2-wp46
- https://github.com/FasterXML/jackson-modules-java8
- https://bugzilla.redhat.com/show_bug.cgi?id=1665601
