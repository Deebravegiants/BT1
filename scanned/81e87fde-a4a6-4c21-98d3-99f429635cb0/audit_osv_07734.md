# [C] Apache Tomcat: EncryptInterceptor requirements not clearly documented

## Summary
Severity: Critical
Advisory: BIT-tomcat-2026-59084
Aliases: CVE-2026-59084
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-59084
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.24

## Details
Insufficient Technical Documentation vulnerability in Apache Tomcat since the requirements to securely configure the EncryptInterceptor were not clearly documented.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.23, from 10.1.0 through 10.1.56, from 9.0.13 through 9.0.119, from 8.5.38 through 8.5.100, from 7.0.100 through 7.0.109. Other versions that have reached end of support may also be affected.

Users are recommended to upgrade to version 11.0.24, 10.1.57 or 9.0.120 which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/14/8
- https://lists.apache.org/thread/7w9746ootcxo0gvx26xjpw80l31f1qw7
- https://nvd.nist.gov/vuln/detail/CVE-2026-59084
