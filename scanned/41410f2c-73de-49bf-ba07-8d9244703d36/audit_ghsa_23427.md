# [M] Exposure of Sensitive Information to an Unauthorized Actor in Direct Web Remoting

## Summary
Severity: Medium
Advisory: GHSA-hqw5-62gp-rqgm
CVE: CVE-2014-5325
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-hqw5-62gp-rqgm
Type: github-advisory

## Affected
- Maven: `org.directwebremoting:dwr` — affected >=0 <2.0.11
- Maven: `org.directwebremoting:dwr` — affected >=3.0.M1 <3.0.RC3

## Details
The (1) DOMConverter, (2) JDOMConverter, (3) DOM4JConverter, and (4) XOMConverter functions in Direct Web Remoting (DWR) through 2.0.10 and 3.x through 3.0.RC2 allow remote attackers to read arbitrary files via DOM data containing an XML external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-5325
- http://jvn.jp/en/jp/JVN91502163/index.html
- http://jvndb.jvn.jp/jvndb/JVNDB-2014-000117
