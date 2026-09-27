# [C] Apache Tomcat: Authentication bypass when using Jakarta Authentication API

## Summary
Severity: Critical
Advisory: BIT-tomcat-2024-52316
Aliases: CVE-2024-52316, GHSA-xcpr-7mr4-h4xq
Ecosystem: Bitnami
Published: 2025-07-10
Source: https://osv.dev/vulnerability/BIT-tomcat-2024-52316
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=10.0.0 <10.1.31

## Details
Unchecked Error Condition vulnerability in Apache Tomcat. If Tomcat is configured to use a custom Jakarta Authentication (formerly JASPIC) ServerAuthContext component which may throw an exception during the authentication process without explicitly setting an HTTP status to indicate failure, the authentication may not fail, allowing the user to bypass the authentication process. There are no known Jakarta Authentication components that behave in this way.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.0, from 10.1.0 through 10.1.30, from 9.0.0 through 9.0.95.

The following versions were EOL at the time the CVE was created but are 
known to be affected: 8.5.0 though 8.5.100. Other EOL versions may also be affected.


Users are recommended to upgrade to version 11.0.0, 10.1.31 or 9.0.96, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/11/18/2
- https://lists.apache.org/thread/lopzlqh91jj9n334g02om08sbysdb928
- https://nvd.nist.gov/vuln/detail/CVE-2024-52316
- https://security.netapp.com/advisory/ntap-20250124-0003/
- https://lists.debian.org/debian-lts-announce/2025/01/msg00009.html
