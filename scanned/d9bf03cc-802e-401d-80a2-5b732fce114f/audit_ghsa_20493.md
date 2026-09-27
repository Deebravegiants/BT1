# [M] Kylin can receive user input and load any class through Class.forName(...).

## Summary
Severity: Medium
Advisory: GHSA-q656-g2x3-8cgh
CVE: CVE-2021-31522
CWE: CWE-470
Ecosystem: Maven
Published: 2022-01-08
Source: https://github.com/advisories/GHSA-q656-g2x3-8cgh
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin` — affected >=0 <3.1.3
- Maven: `org.apache.kylin:kylin` — affected >=4.0.0 <4.0.1

## Details
Kylin can receive user input and load any class through Class.forName(...). This issue affects Apache Kylin 2 version 2.6.6 and prior versions; Apache Kylin 3 version 3.1.2 and prior versions; Apache Kylin 4 version 4.0.0 and prior versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31522
- https://github.com/apache/kylin/pull/1695
- https://github.com/apache/kylin/pull/1763
- https://github.com/apache/kylin
- https://lists.apache.org/thread/hh5crx3yr701zd8wtpqo1mww2rlkvznw
- http://www.openwall.com/lists/oss-security/2022/01/06/4
