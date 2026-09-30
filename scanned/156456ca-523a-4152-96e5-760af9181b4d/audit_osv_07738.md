# [C] Apache Tomcat: Limited replay attack possible with DIGEST authentication

## Summary
Severity: Critical
Advisory: BIT-tomcat-2026-65905
Aliases: CVE-2026-65905, GHSA-9xv2-5v5q-p794
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-65905
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Authentication Bypass by Capture-replay vulnerability in Apache Tomcat's DIGEST authenticator. If, before windowSize requests have been made, a client makes a DIGEST 
authenticated request with a nonceCount on the upper boundary of the 
replay window then that request is replayable once only while the 
associated nonceCount remains within the replay window.



 

This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.0 through 9.0.120.



The following versions were EOL at the time the CVE was created but are 
known to be affected: from 8.5.0 through 8.5.100, from 7.0.30 through 7.0.109. Other unsupported versions may also be affected.



Users are recommended to upgrade to version 11.0.25, 10.1.58 or 9.0.121, which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/4
- https://lists.apache.org/thread/9v114xlpgbzrrbzz5vf9f6r2q4wnxwwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-65905
