# [H] Apache CXF: Denial of Service vulnerability with temporary files

## Summary
Severity: High
Advisory: GHSA-fh5r-crhr-qrrq
CVE: CVE-2025-23184
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-fh5r-crhr-qrrq
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-core` — affected >=0 <3.5.10
- Maven: `org.apache.cxf:cxf-core` — affected >=3.6.0 <3.6.5
- Maven: `org.apache.cxf:cxf-core` — affected >=4.0.0 <4.0.6

## Details
A potential denial of service vulnerability is present in versions of Apache CXF before 3.5.10, 3.6.5 and 4.0.6. In some edge cases, the CachedOutputStream instances may not be closed and, if backed by temporary files, may fill up the file system (it applies to servers and clients).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-23184
- https://github.com/apache/cxf/pull/2048
- https://github.com/apache/cxf/pull/2111
- https://github.com/apache/cxf
- https://issues.apache.org/jira/browse/CXF-7396
- https://lists.apache.org/thread/lfs8l63rnctnj2skfrxyys7v8fgnt122
- https://security.netapp.com/advisory/ntap-20250214-0003
- https://www.vicarius.io/vsociety/posts/cve-2025-23184-detect-apache-cxf-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2025-23184-mitigate-apache-cxf-vulnerability
- http://www.openwall.com/lists/oss-security/2025/01/20/3
