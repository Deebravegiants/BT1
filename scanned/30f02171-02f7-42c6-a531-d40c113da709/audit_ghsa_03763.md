# [C] Polymorphic Typing issue in FasterXML jackson-databind

## Summary
Severity: Critical
Advisory: GHSA-h822-r4r5-v8jg
CVE: CVE-2019-14540
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-23
Source: https://github.com/advisories/GHSA-h822-r4r5-v8jg
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.10
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.7.0 <2.8.11.5
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=0 <2.6.7.3

## Details
A Polymorphic Typing issue was discovered in FasterXML jackson-databind before 2.9.10, 2.8.11.5, and 2.6.7.3. It is related to `com.zaxxer.hikari.HikariConfig`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14540
- https://github.com/FasterXML/jackson-databind/issues/2410
- https://github.com/FasterXML/jackson-databind/issues/2449
- https://github.com/FasterXML/jackson-databind/commit/73c1c2cc76e6cdd7f3a5615cbe3207fe96e4d3db
- https://github.com/FasterXML/jackson-databind/commit/d4983c740fec7d5576b207a8c30a63d3ea7443de
- https://access.redhat.com/errata/RHSA-2019:3200
- https://lists.apache.org/thread.html/f9bc3e55f4e28d1dcd1a69aae6d53e609a758e34d2869b4d798e13cc@%3Cissues.drill.apache.org%3E
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0@%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/r8aaf4ee16bbaf6204731d4770d96ebb34b258cd79b491f9cdd7f2540@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rca37935d661f4689cb4119f1b3b224413b22be161b678e6e6ce0c69b@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/rf1bbc0ea4a9f014cf94df9a12a6477d24a27f52741dbc87f2fd52ff2@%3Cissues.geode.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2019/10/msg00001.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Q7CANA7KV53JROZDX5Z5P26UG5VN2K43
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TH5VFUN4P7CCIP7KSEXYA5MUTFCUDUJT
- https://seclists.org/bugtraq/2019/Oct/6
- https://security.netapp.com/advisory/ntap-20191004-0002
- https://www.debian.org/security/2019/dsa-4542
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
