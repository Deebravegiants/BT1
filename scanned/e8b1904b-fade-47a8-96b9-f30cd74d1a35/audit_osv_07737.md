# [C] Apache Tomcat: HTTP/2 no-authority bypass of strict SNI validation - CVE-2026-32990 fix incomplete

## Summary
Severity: Critical
Advisory: BIT-tomcat-2026-65637
Aliases: CVE-2026-65637
Ecosystem: Bitnami
Published: 2026-08-28
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-65637
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.20 <11.0.25

## Details
Improper Input Validation vulnerability in Apache Tomcat due to incomplete fix for CVE-2026-32990.



This issue affects Apache Tomcat: from 11.0.20 through 11.0.24, from 10.1.53 through 10.1.57, from 9.0.115 through 9.0.120.



Users are recommended to upgrade to version 11.0.25, 10.1.58 or 9.0.121, which fix the issue.

## References
- https://lists.apache.org/thread/djog953z1ohsyt25bdvhfzbmsy22vgcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-65637
