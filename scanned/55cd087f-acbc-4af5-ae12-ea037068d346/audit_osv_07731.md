# [M] Apache Tomcat: Security constraints for default servlet ignored method

## Summary
Severity: Medium
Advisory: BIT-tomcat-2026-55956
Aliases: CVE-2026-55956
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-55956
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.23

## Details
Improper Authorization vulnerability in Apache Tomcat leads to security constraints specified for the default servlet ignoring any method or method omission configured as part of the constraint.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.22, from 10.1.0 through 10.1.55, from 9.0.0 through 9.0.118, from 8.5.0 through 8.5.100, from 7.0.0 through 7.0.109. Other versions that have reached end of support may also be affected.

Users are recommended to upgrade to version 11.0.23, 10.1.56 or 9.0.119, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/25
- https://lists.apache.org/thread/dcjdcnnnww9hhdm016hr0l7hpw1bzjfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-55956
