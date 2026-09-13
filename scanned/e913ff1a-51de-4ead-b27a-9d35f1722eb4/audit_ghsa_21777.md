# [H] Improper synchronization in Apache Netbeans HTML/Java API

## Summary
Severity: High
Advisory: GHSA-ppc3-fpvh-7396
CVE: CVE-2020-17534
CWE: CWE-362
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-ppc3-fpvh-7396
Type: github-advisory

## Affected
- Maven: `org.netbeans.html:pom` — affected >=0 <1.7.1

## Details
There exists a race condition between the deletion of the temporary file and the creation of the temporary directory in `webkit` subproject of HTML/Java API version 1.7. A similar vulnerability has recently been disclosed in other Java projects and the fix in HTML/Java API version 1.7.1 follows theirs: To avoid local privilege escalation version 1.7.1 creates the temporary directory atomically without dealing with the temporary file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17534
- https://github.com/apache/netbeans-html4j/commit/fa70e507e5555e1adb4f6518479fc408a7abd0e6
- https://lists.apache.org/thread.html/ra6119c0cdfccf051a846fa11b61364f5df9e7db93c310706a947f86a%40%3Cdev.netbeans.apache.org%3E
