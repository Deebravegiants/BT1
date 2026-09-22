# [H] Apache Tomcat: DoS via allocation leak in HTTP/2 backlog tracking when a stream is reset

## Summary
Severity: High
Advisory: BIT-tomcat-2026-68763
Aliases: CVE-2026-68763
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-68763
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Uncontrolled Resource Consumption vulnerability in Apache Tomcat via an allocation leak in the HTTP/2 backlog tracking when a stream is reset



This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.39 through 9.0.120.



The following versions were EOL at the time the CVE was created but are 
known to be affected: from 8.5.59 through 8.5.100. Other unsupported versions may also be affected.



Users are recommended to upgrade to version 11.0.25, 10.1.58 or 9.0.121, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/9
- https://lists.apache.org/thread/tv51ty39ppv41v04hdtkp9dp7tg02nzl
- https://nvd.nist.gov/vuln/detail/CVE-2026-68763
