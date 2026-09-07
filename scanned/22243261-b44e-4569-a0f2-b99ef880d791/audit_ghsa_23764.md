# [H] Apache Jackrabbit Authentication Hijacking Vulnerability

## Summary
Severity: High
Advisory: GHSA-9fc7-rhq3-wm7x
CVE: CVE-2016-6801
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9fc7-rhq3-wm7x
Type: github-advisory

## Affected
- Maven: `org.apache.jackrabbit:jackrabbit-webdav` — affected >=2.4.0 <2.4.6
- Maven: `org.apache.jackrabbit:jackrabbit-webdav` — affected >=2.6.0 <2.6.6
- Maven: `org.apache.jackrabbit:jackrabbit-webdav` — affected >=2.8.0 <2.8.3
- Maven: `org.apache.jackrabbit:jackrabbit-webdav` — affected >=2.10.0 <2.10.4
- Maven: `org.apache.jackrabbit:jackrabbit-webdav` — affected >=2.12.0 <2.12.4
- Maven: `org.apache.jackrabbit:jackrabbit-webdav` — affected >=2.13.0 <2.13.3

## Details
Cross-site request forgery (CSRF) vulnerability in the CSRF content-type check in Jackrabbit-Webdav in Apache Jackrabbit 2.4.x before 2.4.6, 2.6.x before 2.6.6, 2.8.x before 2.8.3, 2.10.x before 2.10.4, 2.12.x before 2.12.4, and 2.13.x before 2.13.3 allows remote attackers to hijack the authentication of unspecified victims for requests that create a resource via an HTTP POST request with a (1) missing or (2) crafted Content-Type header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6801
- https://github.com/apache/jackrabbit/commit/16f2f02fcaef6202a2bf24c449d4fd10eb98f08d
- https://github.com/apache/jackrabbit/commit/ea75d7c2aeaafecd9ab97736bf81c5616f703244
- https://github.com/apache/jackrabbit/commit/eae001a54aae9c243ac06b5c8f711b2cb2038700
- https://github.com/apache/jackrabbit
- https://issues.apache.org/jira/browse/JCR-4009
- https://web.archive.org/web/20210123170657/http://www.securityfocus.com/bid/92966
- http://www.debian.org/security/2016/dsa-3679
- http://www.openwall.com/lists/oss-security/2016/09/14/6
