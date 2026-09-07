# [C] Arbitrary Code Execution in jackson-databind

## Summary
Severity: Critical
Advisory: GHSA-645p-88qh-w398
CVE: CVE-2018-14718
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-645p-88qh-w398
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.7
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.8.0 <2.8.11.3
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.7.0 <2.7.9.5
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.0.0 <2.6.7.3

## Details
FasterXML jackson-databind 2.x before 2.9.7, 2.8.11.3, 2.7.9.5, and 2.6.7.3 might allow remote attackers to execute arbitrary code by leveraging failure to block the slf4j-ext class from polymorphic deserialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14718
- https://github.com/FasterXML/jackson-databind/issues/2097
- https://github.com/FasterXML/jackson-databind/commit/87d29af25e82a249ea15858e2d4ecbf64091db44
- https://access.redhat.com/errata/RHBA-2019:0959
- https://lists.apache.org/thread.html/6a78f88716c3c57aa74ec05764a37ab3874769a347805903b393b286@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/82b01bfb6787097427ce97cec6a7127e93718bc05d1efd5eaffc228f@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/ba973114605d936be276ee6ce09dfbdbf78aa56f6cdc6e79bfa7b8df@%3Cdev.lucene.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/r1d4a247329a8478073163567bbc8c8cb6b49c6bfc2bf58153a857af1@%3Ccommits.druid.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2019/03/msg00005.html
- https://seclists.org/bugtraq/2019/May/68
- https://security.netapp.com/advisory/ntap-20190530-0003
- https://www.debian.org/security/2019/dsa-4452
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
