# [H] Apache Tomcat: Principal lookup can fail open in some cases

## Summary
Severity: High
Advisory: BIT-tomcat-2026-68569
Aliases: CVE-2026-68569
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-68569
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Improper Authentication vulnerability in Apache Tomcat meant that in some circumstances (e.g. CLIENT-CERT, SPNEGO) that a user would be authenticated even if the user did not exist in the DataSourceRealm.



This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.0 through 9.0.120.







The following versions were EOL at the time the CVE was created but are 
known to be affected: from 8.5.0 through 8.5.100, from 7.0.0 through 7.0.109. Other unsupported versions may also be affected.







Users are recommended to upgrade to version 11.0.25, 10.1.58 or 9.0.121, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/8
- https://lists.apache.org/thread/8robqo76q0osxgw0b5lcwgz0hcf9h4zc
- https://nvd.nist.gov/vuln/detail/CVE-2026-68569
