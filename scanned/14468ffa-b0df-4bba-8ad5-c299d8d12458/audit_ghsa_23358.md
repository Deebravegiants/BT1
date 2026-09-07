# [M] Improper Neutralization of Input During Web Page Generation in Apache Solr

## Summary
Severity: Medium
Advisory: GHSA-wgw2-gw4v-9w4j
CVE: CVE-2014-3628
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wgw2-gw4v-9w4j
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr` — affected >=4.0.0 <4.10.3

## Details
Cross-site scripting (XSS) vulnerability in the Admin UI Plugin / Stats page in Apache Solr 4.x before 4.10.3 allows remote attackers to inject arbitrary web script or HTML via the fieldvaluecache object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3628
- http://mail-archives.us.apache.org/mod_mbox/www-announce/201412.mbox/%3C54A1A7C7.2070804@apache.org%3E
