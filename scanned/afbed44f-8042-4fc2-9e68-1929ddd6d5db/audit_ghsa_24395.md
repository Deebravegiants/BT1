# [M] XWork in Apache Struts Reveals Sensitive Information

## Summary
Severity: Medium
Advisory: GHSA-9ccm-g362-2r35
CVE: CVE-2011-2088
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-9ccm-g362-2r35
Type: github-advisory

## Affected
- Maven: `org.apache.struts.xwork:xwork-core` — affected >=0 <2.2.2

## Details
XWork 2.2.1 in Apache Struts 2.2.1, and OpenSymphony XWork in OpenSymphony WebWork, allows remote attackers to obtain potentially sensitive information about internal Java class paths via vectors involving an s:submit element and a nonexistent method, a different vulnerability than CVE-2011-1772.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-2088
- https://github.com/apache/struts/commit/885ab3459e146ff830d1f7257f809f4a3dd4493a
- https://issues.apache.org/jira/browse/WW-3579
- https://web.archive.org/web/20110726113612/http://www.ventuneac.net/security-advisories/MVSA-11-006
- https://web.archive.org/web/20201207174744/http://www.securityfocus.com/archive/1/518066/100/0/threaded
- http://secureappdev.blogspot.com/2011/05/apache-struts-2-xwork-webwork-reflected.html
