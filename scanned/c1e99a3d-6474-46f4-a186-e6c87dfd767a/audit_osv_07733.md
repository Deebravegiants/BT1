# [C] Apache Tomcat: Incorrect URL decoding in RewriteValve may allow security control bypass

## Summary
Severity: Critical
Advisory: BIT-tomcat-2026-59083
Aliases: CVE-2026-59083
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-59083
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.24

## Details
Improper Handling of URL Encoding (Hex Encoding) vulnerability in Apache Tomcat's rewrite valve allowed security constraint bypass for some configurations.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.23, from 10.1.0 through 10.1.56, from 9.0.0 through 9.0.119, from 8.5.0 through 8.5.100. Other versions that have reached end of support may also be affected.

Users are recommended to upgrade to version 11.0.24, 10.1.57 or 9.0.120, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/14/7
- https://lists.apache.org/thread/3g63zos2gkjo5vgnrk8kxmosv47w6wbq
- https://nvd.nist.gov/vuln/detail/CVE-2026-59083
