# [C] Improper Restriction of XML External Entity Reference in Jelly

## Summary
Severity: Critical
Advisory: GHSA-6g33-82gc-3pw5
CVE: CVE-2017-12621
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6g33-82gc-3pw5
Type: github-advisory

## Affected
- Maven: `commons-jelly:commons-jelly` — affected >=0 <1.0.1

## Details
During Jelly (xml) file parsing with Apache Xerces, if a custom doctype entity is declared with a "SYSTEM" entity with a URL and that entity is used in the body of the Jelly file, during parser instantiation the parser will attempt to connect to said URL. This could lead to XML External Entity (XXE) attacks in Apache Commons Jelly before 1.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12621
- https://github.com/apache/commons-jelly
- https://issues.apache.org/jira/browse/JELLY-293
- https://lists.apache.org/thread.html/f1fc3f2c45264af44ce782d54b5908ac95f02bf7ad88bb57bfb04b73@%3Cdev.commons.apache.org%3E
- https://web.archive.org/web/20200227144849/http://www.securityfocus.com/bid/101052
- https://web.archive.org/web/20210303081618/http://www.securitytracker.com/id/1039444
