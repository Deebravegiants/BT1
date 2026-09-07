# [M] Apache Axis2 Vulnerable to XML Signature wrapping attack

## Summary
Severity: Medium
Advisory: GHSA-88r4-38gc-97p4
CVE: CVE-2012-4418
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-88r4-38gc-97p4
Type: github-advisory

## Affected
- Maven: `org.apache.axis2:axis2` — affected >=0 <1.7.9

## Details
Apache Axis2 allows remote attackers to forge messages and bypass authentication via an "XML Signature wrapping attack."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4418
- https://bugzilla.redhat.com/show_bug.cgi?id=856755
- https://github.com/apache/axis-axis2-java-core
- https://issues.apache.org/jira/browse/AXIS2-5930
- https://issues.apache.org/jira/browse/AXIS2C-1694
- https://web.archive.org/web/20121114075457/http://www.securityfocus.com/bid/55508
- http://www.nds.rub.de/media/nds/veroeffentlichungen/2012/08/22/BreakingSAML_3.pdf
- http://www.openwall.com/lists/oss-security/2012/09/12/1
- http://www.openwall.com/lists/oss-security/2012/09/13/1
