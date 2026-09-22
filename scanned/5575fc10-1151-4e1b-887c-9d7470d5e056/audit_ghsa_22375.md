# [M] Path Traversal in Apache Oozie

## Summary
Severity: Medium
Advisory: GHSA-2fx6-r6qx-3c7h
CVE: CVE-2017-15712
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-2fx6-r6qx-3c7h
Type: github-advisory

## Affected
- Maven: `org.apache.oozie:oozie-core` — affected >=3.1.3 <5.0.0

## Details
Vulnerability allows a user of Apache Oozie 3.1.3-incubating to 4.3.0 and 5.0.0-beta1 to expose private files on the Oozie server process. The malicious user can construct a workflow XML file containing XML directives and configuration that reference sensitive files on the Oozie server host.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15712
- https://lists.apache.org/thread.html/4606709264fe7cb0285e2a12aca2d01a06b14cd58791c9fc32abd216@%3Cdev.oozie.apache.org%3E
- http://www.securityfocus.com/bid/103102
