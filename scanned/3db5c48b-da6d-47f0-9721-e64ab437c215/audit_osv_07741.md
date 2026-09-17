# [H] Apache Tomcat: Servlet role references can bypass declarative role constraints

## Summary
Severity: High
Advisory: BIT-tomcat-2026-66422
Aliases: CVE-2026-66422
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-66422
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Improper Authorization vulnerability in Apache Tomcat cause by security-role-ref definitions being incorrectly used as role aliases within the Realm in additional to the correct usage with Request.isUserInRole().



This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.25 through 9.0.120.



The following versions were EOL at the time the CVE was created but are 
known to be affected: from 8.5.46 through 8.5.100, from 7.0.97 through 7.0.109. Other unsupported versions may also be affected.



Users are recommended to upgrade to version 11.0.25, 10.1.58 or 9.0.121, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/6
- https://lists.apache.org/thread/j5plylz1b2vhqvbkqn7k58nygxhcpk73
- https://nvd.nist.gov/vuln/detail/CVE-2026-66422
