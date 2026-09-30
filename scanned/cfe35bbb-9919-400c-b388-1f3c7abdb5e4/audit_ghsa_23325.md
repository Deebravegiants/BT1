# [H] Improper Control of Generation of Code in Apache Struts

## Summary
Severity: High
Advisory: GHSA-whmq-v94q-34p9
CVE: CVE-2013-1965
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-whmq-v94q-34p9
Type: github-advisory

## Affected
- Maven: `org.apache.struts:struts2-core` — affected >=0 <2.3.14.3

## Details
Apache Struts Showcase App 2.0.0 through 2.3.13, as used in Struts 2 before 2.3.14.3, allows remote attackers to execute arbitrary OGNL code via a crafted parameter name that is not properly handled when invoking a redirect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1965
- https://github.com/apache/struts/commit/7e6f641ebb142663cbd1653dc49bed725edf7f56
- https://bugzilla.redhat.com/show_bug.cgi?id=967655
- https://github.com/apache/struts
- https://web.archive.org/web/20140227231557/http://www.securityfocus.com/bid/60082
- http://struts.apache.org/development/2.x/docs/s2-012.html
