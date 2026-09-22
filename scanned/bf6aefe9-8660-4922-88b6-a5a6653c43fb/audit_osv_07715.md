# [C] Apache Tomcat: RCE due to TOCTOU issue in JSP compilation

## Summary
Severity: Critical
Advisory: BIT-tomcat-2024-50379
Aliases: CVE-2024-50379, GHSA-5j33-cvvr-w245
Ecosystem: Bitnami
Published: 2025-07-10
Source: https://osv.dev/vulnerability/BIT-tomcat-2024-50379
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.2

## Details
Time-of-check Time-of-use (TOCTOU) Race Condition vulnerability during JSP compilation in Apache Tomcat permits an RCE on case insensitive file systems when the default servlet is enabled for write (non-default configuration).

This issue affects Apache Tomcat: from 11.0.0 through 11.0.1, from 10.1.0 through 10.1.33, from 9.0.0 through 9.0.97.

The following versions were EOL at the time the CVE was created but are 
known to be affected: 8.5.0 though 8.5.100. Other, older, EOL versions may also be affected.

Users are recommended to upgrade to version 11.0.2, 10.1.34 or 9.0.98, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/12/17/4
- http://www.openwall.com/lists/oss-security/2024/12/18/2
- https://lists.apache.org/thread/y6lj6q1xnp822g6ro70tn19sgtjmr80r
- https://nvd.nist.gov/vuln/detail/CVE-2024-50379
- https://security.netapp.com/advisory/ntap-20250103-0003/
- https://lists.debian.org/debian-lts-announce/2025/01/msg00009.html
