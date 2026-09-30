# [C] Improper Input Validation in jackson-databind

## Summary
Severity: Critical
Advisory: GHSA-f3j5-rmmp-3fc5
CVE: CVE-2019-17267
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-f3j5-rmmp-3fc5
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.10
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=0 <2.8.11.5

## Details
A Polymorphic Typing issue was discovered in FasterXML jackson-databind before 2.9.10 and 2.8.11.5. It is related to net.sf.ehcache.hibernate.EhcacheJtaTransactionManagerLookup.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17267
- https://github.com/FasterXML/jackson-databind/issues/2460
- https://github.com/FasterXML/jackson-databind/commit/191a4cdf87b56d2ddddb77edd895ee756b7f75eb
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://security.netapp.com/advisory/ntap-20191017-0006
- https://lists.debian.org/debian-lts-announce/2019/12/msg00013.html
- https://lists.apache.org/thread.html/rf1bbc0ea4a9f014cf94df9a12a6477d24a27f52741dbc87f2fd52ff2@%3Cissues.geode.apache.org%3E
- https://lists.apache.org/thread.html/r9d727fc681fb3828794acbefcaee31393742b4d73a29461ccd9597a8@%3Cdev.skywalking.apache.org%3E
- https://lists.apache.org/thread.html/r392099ed2757ff2e383b10440594e914d080511d7da1c8fed0612c1f@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0@%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f@%3Cdev.drill.apache.org%3E
- https://github.com/FasterXML/jackson-databind/compare/jackson-databind-2.9.9.3...jackson-databind-2.9.10
- https://github.com/FasterXML/jackson-databind
- https://access.redhat.com/errata/RHSA-2020:0445
- https://access.redhat.com/errata/RHSA-2020:0164
- https://access.redhat.com/errata/RHSA-2020:0161
