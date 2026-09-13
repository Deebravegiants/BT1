# [H] Apache Tomcat: HTTP/2 excess header handling DoS

## Summary
Severity: High
Advisory: BIT-tomcat-2024-34750
Aliases: CVE-2024-34750, GHSA-wm9w-rjj3-j356
Ecosystem: Bitnami
Published: 2025-07-29
Source: https://osv.dev/vulnerability/BIT-tomcat-2024-34750
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=10.0.0 <10.1.25

## Details
Improper Handling of Exceptional Conditions, Uncontrolled Resource Consumption vulnerability in Apache Tomcat. When processing an HTTP/2 stream, Tomcat did not handle some cases of excessive HTTP headers correctly. This led to a miscounting of active HTTP/2 streams which in turn led to the use of an incorrect infinite timeout which allowed connections to remain open which should have been closed.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.0, from 10.1.0 through 10.1.24, from 9.0.0 through 9.0.89.

The following versions were EOL at the time the CVE was created but are 
known to be affected: 8.5.0 though 8.5.100. Other EOL versions may also be affected.


Users are recommended to upgrade to version 11.0.0, 10.1.25 or 9.0.90, which fixes the issue.

## References
- https://lists.apache.org/thread/4kqf0bc9gxymjc2x7v3p7dvplnl77y8l
- https://nvd.nist.gov/vuln/detail/CVE-2024-34750
- https://security.netapp.com/advisory/ntap-20240816-0004/
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
- https://github.com/apache/tomcat/commit/2344a4c0d03e307ba6b8ab6dc8b894cc8bac63f2
- https://github.com/apache/tomcat/commit/2afae300c9ac9c0e516e2e9de580847d925365c3
- https://github.com/apache/tomcat/commit/9fec9a82887853402833a80b584e3762c7423f5f
