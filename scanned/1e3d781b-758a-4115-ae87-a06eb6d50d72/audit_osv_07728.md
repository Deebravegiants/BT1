# [C] Apache Tomcat: Invalid CRL configuration doesn't trigger failure for FFM Connector

## Summary
Severity: Critical
Advisory: BIT-tomcat-2026-53434
Aliases: CVE-2026-53434
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-53434
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.5

## Details
Detection of Error Condition Without Action vulnerability in Apache Tomcat when configuring CRLs for a FFM based connector.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.22, from 10.1.0 through 10.1.55, from 9.0.83 through 9.0.118.

Users are recommended to upgrade to version 11.0.23, 10.1.56 or 9.0.119, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/22
- https://lists.apache.org/thread/x510lbq0sfrd1qyo7q3r1mpllgpdcosk
- https://nvd.nist.gov/vuln/detail/CVE-2026-53434
