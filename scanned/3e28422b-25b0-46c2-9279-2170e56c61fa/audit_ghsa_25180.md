# [M] Apache Sling Auth Core bundle vulnerable to Open Redirection

## Summary
Severity: Medium
Advisory: GHSA-j7f2-cqvq-5jcf
CVE: CVE-2013-4390
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j7f2-cqvq-5jcf
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.auth.core` — affected >=0 <1.1.4

## Details
Open redirect vulnerability in the AbstractAuthenticationFormServlet in the Auth Core (org.apache.sling.auth.core) bundle before 1.1.4 in Apache Sling allows remote attackers to redirect users to arbitrary web sites and conduct phishing attacks via a URL in the resource parameter, related to "a custom login form and XSS."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4390
- https://github.com/apache/sling-org-apache-sling-auth-core/commit/d1cd9aaa3432d577b65c50b3fbdc36d5d667ca46
- https://github.com/apache/sling-org-apache-sling-auth-core
- https://issues.apache.org/jira/browse/SLING-3141
- http://mail-archives.apache.org/mod_mbox/sling-dev/201310.mbox/%3CCAKkCf4qdFxEW9NXBJoMsrBama8LFNyir%2B61A0Vfzp4njEpeU%3Dw%40mail.gmail.com%3E
- http://secunia.com/advisories/55249
- http://www.securityfocus.com/bid/63241
