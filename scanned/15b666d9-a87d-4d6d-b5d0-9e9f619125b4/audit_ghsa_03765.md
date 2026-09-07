# [H] OS Command Injection in Nexus Yum Repository Plugin

## Summary
Severity: High
Advisory: GHSA-g5m7-57ph-j6p8
CVE: CVE-2019-5475
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-11
Source: https://github.com/advisories/GHSA-g5m7-57ph-j6p8
Type: github-advisory

## Affected
- Maven: `org.sonatype.nexus.plugins:nexus-yum-repository-plugin` — affected >=0 <2.14.14

## Details
The Nexus Yum Repository Plugin in v2 is vulnerable to Remote Code Execution when instances using CommandLineExecutor.java are supplied vulnerable data, such as the Yum Configuration Capability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5475
- https://hackerone.com/reports/654888
