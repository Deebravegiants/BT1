# [H] LZ4 Java Compression has Out-of-bounds memory operations which can cause DoS

## Summary
Severity: High
Advisory: GHSA-vqf4-7m7x-wgfc
CVE: CVE-2025-12183
CWE: CWE-125
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-28
Source: https://github.com/advisories/GHSA-vqf4-7m7x-wgfc
Type: github-advisory

## Affected
- Maven: `at.yawk.lz4:lz4-java` — affected >=0 <1.8.1
- Maven: `org.lz4:lz4-java` — affected >=0 <1.8.1
- Maven: `org.lz4:lz4-pure-java` — affected >=0
- Maven: `net.jpountz.lz4:lz4` — affected >=0

## Details
Out-of-bounds memory operations in org.lz4:lz4-java 1.8.0 and earlier allow remote attackers to cause denial of service and read adjacent memory via untrusted compressed input.

This is fixed in a forked release: at.yawk.lz4:lz4-java version 1.8.1. The original project has been archived: https://github.com/lz4/lz4-java, and Sonatype has added a redirect from org.lz4:lz4-java:1.8.1 to the new group ID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-12183
- https://github.com/yawkat/lz4-java
- https://github.com/yawkat/lz4-java/releases/tag/v1.8.1
- https://sites.google.com/sonatype.com/vulnerabilities/cve-2025-12183
- https://www.sonatype.com/security-advisories/cve-2025-12183
- http://www.openwall.com/lists/oss-security/2025/12/01/5
