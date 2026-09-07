# [M] Apache Jackrabbit contains Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-6fxv-38xc-h866
CVE: CVE-2009-0026
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-6fxv-38xc-h866
Type: github-advisory

## Affected
- Maven: `org.apache.jackrabbit:jackrabbit` — affected >=0 <1.5.2

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Apache Jackrabbit before 1.5.2 allow remote attackers to inject arbitrary web script or HTML via the q parameter to (1) search.jsp or (2) swr.jsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-0026
- https://github.com/apache/jackrabbit/commit/36330ae8df40ceaddf9f3f95b8d4855b54921579
- https://github.com/apache/jackrabbit/commit/fbdcc02bc35db1d23b527da7bc411087ef29bf1f
- https://access.redhat.com/security/cve/CVE-2009-0026
- https://bugzilla.redhat.com/show_bug.cgi?id=481126
- https://exchange.xforce.ibmcloud.com/vulnerabilities/48110
- https://issues.apache.org/jira/browse/JCR-1925
- https://www.apache.org/dist/jackrabbit/RELEASE-NOTES-1.5.2.txt
- https://www.vupen.com/english/advisories/2009/0177
