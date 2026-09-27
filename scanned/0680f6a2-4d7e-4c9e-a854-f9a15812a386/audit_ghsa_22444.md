# [H] Apache Sling JCR ContentLoader XmlReader Arbitrary File Load

## Summary
Severity: High
Advisory: GHSA-wjp3-4xcq-598p
CVE: CVE-2012-3353
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wjp3-4xcq-598p
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.jcr.contentloader` — affected >=0 <2.1.6

## Details
The Apache Sling JCR ContentLoader 2.1.4 XmlReader used in the Sling JCR content loader module makes it possible to import arbitrary files in the content repository, including local files, causing potential information leaks. Users should upgrade to version 2.1.6 of the JCR ContentLoader

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3353
- https://issues.apache.org/jira/browse/SLING-2512
- https://lists.apache.org/thread/owd2xw86l19dh1f1zlhq41l7wlnd16sk
