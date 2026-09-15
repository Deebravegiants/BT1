# [C] Apache Tomcat: Bypass of rules in Rewrite Valve

## Summary
Severity: Critical
Advisory: BIT-tomcat-2025-31651
Aliases: CVE-2025-31651, GHSA-ff77-26x5-69cr
Ecosystem: Bitnami
Published: 2025-07-10
Source: https://osv.dev/vulnerability/BIT-tomcat-2025-31651
Type: osv

## Affected
- Bitnami: `tomcat` — affected >=11.0.0 <11.0.6

## Details
Improper Neutralization of Escape, Meta, or Control Sequences vulnerability in Apache Tomcat. For a subset of unlikely rewrite rule configurations, it was possible 
for a specially crafted request to bypass some rewrite rules. If those 
rewrite rules effectively enforced security constraints, those 
constraints could be bypassed.

This issue affects Apache Tomcat: from 11.0.0 through 11.0.5, from 10.1.0 through 10.1.39, from 9.0.0 through 9.0.102.
The following versions were EOL at the time the CVE was created but are 
known to be affected: 8.5.0 though 8.5.100. Other, older, EOL versions 
may also be affected.


Users are recommended to upgrade to version [FIXED_VERSION], which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/04/28/3
- https://lists.apache.org/list.html?announce@tomcat.apache.org
- https://nvd.nist.gov/vuln/detail/CVE-2025-31651
- https://lists.debian.org/debian-lts-announce/2025/07/msg00009.html
