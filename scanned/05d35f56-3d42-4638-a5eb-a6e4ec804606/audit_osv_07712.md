# [H] Apache Tomcat: HTTP request smuggling via malformed trailer headers

## Summary
Severity: High
Advisory: BIT-tomcat-2023-46589
Aliases: CVE-2023-46589, GHSA-fccv-jmmp-qg76
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-tomcat-2023-46589
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=10.1.0 <10.1.16

## Details
Improper Input Validation vulnerability in Apache Tomcat.Tomcat from 11.0.0 through 11.0.0, from 10.1.0 through 10.1.15, from 9.0.0 through 9.0.82 and from 8.5.0 through 8.5.95 did not correctly parse HTTP trailer headers. A trailer header that exceeded the header size limit could cause Tomcat to treat a single 
request as multiple requests leading to the possibility of request 
smuggling when behind a reverse proxy.


Older, EOL versions may also be affected.


Users are recommended to upgrade to version 11.0.0 onwards, 10.1.16 onwards, 9.0.83 onwards or 8.5.96 onwards, which fix the issue.

## References
- https://lists.apache.org/thread/0rqq6ktozqc42ro8hhxdmmdjm1k1tpxr
- https://lists.debian.org/debian-lts-announce/2024/01/msg00001.html
- https://security.netapp.com/advisory/ntap-20231214-0009/
- https://www.openwall.com/lists/oss-security/2023/11/28/2
- https://nvd.nist.gov/vuln/detail/CVE-2023-46589
