# [H] Apache Tomcat: Authentication bypass with JNDIRealm and GSSAPI authenticated bind

## Summary
Severity: High
Advisory: BIT-tomcat-2026-55957
Aliases: CVE-2026-55957
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-55957
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.5

## Details
Missing Critical Step in Authentication vulnerability in Apache Tomcat when the JNDIRealm was configured to authenticate binds using GSSAPI allowed attackers to authenticate without provided the correct password.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.4, from 10.1.0 through 10.1.36, from 9.0.0 through 9.0.100, from 8.5.0 through 8.5.100, from 7.0.0 through 7.0.109.

Users are recommended to upgrade to version 11.0.5, 10.1.37 or 9.0.101, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/26
- https://lists.apache.org/thread/7fk339o5jvd4mcgsf0chbrn4o525ccjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-55957
