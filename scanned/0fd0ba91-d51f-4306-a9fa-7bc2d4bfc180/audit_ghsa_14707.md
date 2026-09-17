# [C] Apache Struts file upload logic is flawed

## Summary
Severity: Critical
Advisory: GHSA-43mq-6xmg-29vm
CVE: CVE-2024-53677
CWE: CWE-22, CWE-434, CWE-915
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-12-11
Source: https://github.com/advisories/GHSA-43mq-6xmg-29vm
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <6.4.0

## Details
File upload logic is flawed vulnerability in Apache Struts. An attacker can manipulate file upload params to enable paths traversal and under some circumstances this can lead to uploading a malicious file which can be used to perform Remote Code Execution.

This issue affects Apache Struts: from 2.0.0 before 6.4.0.

Users are recommended to upgrade to version 6.4.0 at least and migrate to the new file upload mechanism https://struts.apache.org/core-developers/file-upload. If you are not using an old file upload logic based on FileuploadInterceptor your application is safe.

You can find more details in  https://cwiki.apache.org/confluence/display/WW/S2-067 .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53677
- https://github.com/apache/struts/commit/1ecfbae46543a83e131404f8dcc84b3d0d554854
- https://github.com/apache/struts/commit/3ef9ade8902a63bb560892453eeca02bfddefc78
- https://github.com/apache/struts/commit/930fef7679d7247db9e460c146b1698a9d7ad1e4
- https://cwiki.apache.org/confluence/display/WW/S2-067
- https://github.com/apache/struts
- https://security.netapp.com/advisory/ntap-20250103-0005
- https://struts.apache.org/core-developers/file-upload
- https://www.dynatrace.com/news/blog/the-anatomy-of-broken-apache-struts-2-a-technical-deep-dive-into-cve-2024-53677
