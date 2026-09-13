# [M] Apache Syncope JEXL Code Injection

## Summary
Severity: Medium
Advisory: GHSA-r2xf-w5pj-9pw8
CVE: CVE-2014-0111
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r2xf-w5pj-9pw8
Type: github-advisory

## Affected
- Maven: `org.apache.syncope:syncope` — affected >=1.0.0 <1.0.9
- Maven: `org.apache.syncope:syncope` — affected >=1.1.0 <1.1.7

## Details
Apache Syncope 1.0.0 before 1.0.9 and 1.1.0 before 1.1.7 allows remote administrators to execute arbitrary Java code via vectors related to Apache Commons JEXL expressions, "derived schema definition," "user / role templates," and "account links of resource mappings."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0111
- https://web.archive.org/web/20201208163011/http://www.securityfocus.com/archive/1/531841/100/0/threaded
- http://mail-archives.us.apache.org/mod_mbox/www-announce/201404.mbox/%3C534CE273.9020601@apache.org%3E
- http://syncope.apache.org/security.html
