# [M] Apache Tomcat: Authenticated WebSocket session survives end of HTTP session

## Summary
Severity: Medium
Advisory: BIT-tomcat-2026-73180
Aliases: CVE-2026-73180
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-73180
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Insufficient Session Expiration vulnerability in Apache Tomcat meant that if the session ID for an authenticated HTTP session was changed after a WebSocket connection had been established under that authenticated HTTP session, the WebSokcet session would not be closed as required by the Jakarta WebSocket specification when the HTTP session ended.



This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.0 through 9.0.120.



The following versions were EOL at the time the CVE was created but are 
known to be affected: from 8.5.0 through 8.5.100, from 7.0.43 through 7.0.109. Other unsupported versions may also be affected.



Users are recommended to upgrade to version 11.0.25, 10.1.58 or 9.0.121, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/10
- https://lists.apache.org/thread/3j15vztszpyqss253mjq5v1kp7s6hooq
- https://nvd.nist.gov/vuln/detail/CVE-2026-73180
