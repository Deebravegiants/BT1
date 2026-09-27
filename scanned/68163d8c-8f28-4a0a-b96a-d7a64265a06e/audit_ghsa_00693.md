# [H] Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-6wqp-v4v6-c87c
CVE: CVE-2018-12023
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-6wqp-v4v6-c87c
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.7.0 <2.7.9.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.8.0 <2.8.11.2
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.6

## Details
An issue was discovered in FasterXML jackson-databind prior to 2.7.9.4, 2.8.11.2, and 2.9.6. When Default Typing is enabled (either globally or for a specific property), the service has the Oracle JDBC jar in the classpath, and an attacker can provide an LDAP service to access, it is possible to make the service execute a malicious payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12023
- https://github.com/FasterXML/jackson-databind/issues/2058
- https://github.com/FasterXML/jackson-databind/commit/7487cf7eb14be2f65a1eb108e8629c07ef45e0a
- https://github.com/FasterXML/jackson-databind/commit/28badf7ef60ac3e7ef151cd8e8ec010b8479226a
- https://github.com/FasterXML/jackson-databind/commit/bf261d404c2f79fd3406237710d40ebb03c99d84
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/7fcf88aff0d1deaa5c3c7be8d58c05ad7ad5da94b59065d8e7c50c5d@%3Cissues.lucene.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZEDLDUYBSTDY4GWDBUXGJNS2RFYTFVRC
- https://seclists.org/bugtraq/2019/May/68
- https://security.netapp.com/advisory/ntap-20190530-0003
- https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE.pdf
- https://www.debian.org/security/2019/dsa-4452
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
