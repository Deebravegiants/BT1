# [M] Apache Syncope: Stored XSS in Console and Enduser

## Summary
Severity: Medium
Advisory: GHSA-jmrf-85g8-x8xv
CVE: CVE-2024-45031
CWE: CWE-20, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-24
Source: https://github.com/advisories/GHSA-jmrf-85g8-x8xv
Type: github-advisory

## Affected
- Maven: `org.apache.syncope.client:syncope-client-console` — affected >=2.1.0

## Details
When editing objects in the Syncope Console, incomplete HTML tags could be used to bypass HTML sanitization. This made it possible to inject stored XSS payloads which would trigger for other users during ordinary usage of the application.
XSS payloads could also be injected in Syncope Enduser when editing “Personal Information” or “User Requests”: such payloads would trigger for administrators in Syncope Console, thus enabling session hijacking.

Users are recommended to upgrade to version 3.0.9, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45031
- https://github.com/apache/syncope/commit/0c620a9eda2c0927875c129ebae66d2ea94f3e6a
- https://github.com/apache/syncope/commit/f80d3f6cfbd71acb03ece0f7601f660ee0be7e74
- https://github.com/apache/syncope
- https://lists.apache.org/thread/fn567pfmo3s55ofkc42drz8b4kgbhp9m
- https://syncope.apache.org/security#cve-2024-45031-apache-syncope-stored-xss-in-console-and-enduser
- http://www.openwall.com/lists/oss-security/2024/10/24/2
