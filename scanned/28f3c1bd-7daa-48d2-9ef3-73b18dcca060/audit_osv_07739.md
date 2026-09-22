# [H] Apache Tomcat: RewriteValve [N] restarts at the second rule and may bypass access control

## Summary
Severity: High
Advisory: BIT-tomcat-2026-65927
Aliases: CVE-2026-65927
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-tomcat-2026-65927
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.25

## Details
Off-by-one Error vulnerability in Apache Tomcat impacting the [N] flag on the rewrite valves causes rewrite processing to restart at the second rule rather than the first rule.







This issue affects Apache Tomcat: from 11.0.0 through 11.0.24, from 10.1.0 through 10.1.57, from 9.0.0 through 9.0.120.



The following versions were EOL at the time the CVE was created but are 
known to be affected: from 8.5.0 through 8.5.100. Other unsupported versions may also be affected.



Users are recommended to upgrade to version 11.0.25, 10.1.58 or 9.0.121 which fix the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/26/5
- https://lists.apache.org/thread/st1dx1zyn5y7ny2s0sscmh6lrv3worr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-65927
