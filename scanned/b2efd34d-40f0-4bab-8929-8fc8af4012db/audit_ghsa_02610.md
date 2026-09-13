# [C] Remote Code Execution in Any23

## Summary
Severity: Critical
Advisory: GHSA-99px-7724-484v
CVE: CVE-2021-40146
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-13
Source: https://github.com/advisories/GHSA-99px-7724-484v
Type: github-advisory

## Affected
- Maven: `org.apache.any23:apache-any23` — affected >=0 <2.5

## Details
A Remote Code Execution (RCE) vulnerability was discovered in the Any23 YAMLExtractor.java file and is known to affect Any23 versions < 2.5. RCE vulnerabilities allow a malicious actor to execute any code of their choice on a remote machine over LAN, WAN, or internet. RCE belongs to the broader class of arbitrary code execution (ACE) vulnerabilities.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40146
- https://github.com/apache/any23
- https://lists.apache.org/thread.html/r7c521ed85c7ae1bad4fdf95b459f2aaa8a67eae338636b7b7ec35d86%40%3Cannounce.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/09/11/2
