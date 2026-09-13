# [C] jackson-databind vulnerable to remote code execution due to incorrect deserialization and blocklist bypass

## Summary
Severity: Critical
Advisory: GHSA-rfx6-vp9g-rh7v
CVE: CVE-2017-17485
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-rfx6-vp9g-rh7v
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.8.0 <2.8.11
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=0 <2.7.9.2

## Details
FasterXML jackson-databind through 2.8.10 and 2.9.x through 2.9.3 allows unauthenticated remote code execution because of an incomplete fix for the CVE-2017-7525 deserialization flaw. This is exploitable by sending maliciously crafted JSON input to the readValue method of the ObjectMapper, bypassing a blacklist that is ineffective if the Spring libraries are available in the classpath.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-17485
- https://github.com/FasterXML/jackson-databind/issues/1855
- https://github.com/FasterXML/jackson-databind/commit/10fe7f17ea7c8da2a71e7a0c774b420a1d5c1b50
- https://github.com/FasterXML/jackson-databind/commit/2235894210c75f624a3d0cd60bfb0434a20a18bf
- https://github.com/FasterXML/jackson-databind/commit/459107dccc9b3ea991af3e6ad0953e54b01ef7c1
- https://github.com/FasterXML/jackson-databind/commit/4f16f67ebd22c7522fdbb8a7eb87e3026a807d61
- https://github.com/FasterXML/jackson-databind/commit/978798382ceb72229e5036aa1442943933d6d171
- https://github.com/FasterXML/jackson-databind/commit/f031f27a31625d07922bdd090664c69544200a5d
- https://github.com/FasterXML/jackson-databind/commit/eb217dd0f87c5fb471e0668575644aa7eba9a3d3
- https://github.com/FasterXML/jackson-databind/commit/bb45fb16709018842f858f1a6e1118676aaa34bd
- https://github.com/FasterXML/jackson-databind
- https://github.com/irsl/jackson-rce-via-spel
- https://security.netapp.com/advisory/ntap-20180201-0003
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03902en_us
- https://web.archive.org/web/20200927162225/http://www.securityfocus.com/archive/1/541652/100/0/threaded
- https://www.debian.org/security/2018/dsa-4114
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://access.redhat.com/errata/RHSA-2018:0116
- https://access.redhat.com/errata/RHSA-2018:0342
- https://access.redhat.com/errata/RHSA-2018:0478
