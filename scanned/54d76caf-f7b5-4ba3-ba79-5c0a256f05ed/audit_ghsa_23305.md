# [M] Apache Solr Cross-site scripting Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4fxw-g29w-r8mx
CVE: CVE-2015-8796
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4fxw-g29w-r8mx
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr` — affected >=0 <5.3

## Details
Cross-site scripting (XSS) vulnerability in `webapp/web/js/scripts/schema-browser.js` in the Admin UI in Apache Solr before 5.3 allows remote attackers to inject arbitrary web script or HTML via a crafted schema-browse URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8796
- https://github.com/apache/lucene/commit/dc2f2295e0a6c6574f033f295dc0c9adb7660df9
- https://github.com/apache/solr/commit/dc2f2295e0a6c6574f033f295dc0c9adb7660df9
- https://github.com/apache/solr
- https://issues.apache.org/jira/browse/SOLR-7920
- https://web.archive.org/web/20200227160406/http://www.securityfocus.com/bid/85205
