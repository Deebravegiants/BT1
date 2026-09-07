# [C] RichFaces vulnerable to Expression Language Injection

## Summary
Severity: Critical
Advisory: GHSA-3hx6-fqpj-xfjr
CVE: CVE-2018-12532
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-3hx6-fqpj-xfjr
Type: github-advisory

## Affected
- Maven: `org.richfaces:richfaces-core` — affected >=4.5.3.Final

## Details
JBoss RichFaces 4.5.3 through 4.5.17 allows unauthenticated remote attackers to inject an arbitrary expression language (EL) variable mapper and execute arbitrary Java code via a MediaOutputResource's resource request, aka RF-14309.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12532
- https://codewhitesec.blogspot.com/2018/05/poor-richfaces.html
- http://seclists.org/fulldisclosure/2020/Mar/21
