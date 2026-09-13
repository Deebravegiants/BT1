# [H] Apache Shiro Interpretation Conflict vulnerability

## Summary
Severity: High
Advisory: GHSA-7cxr-h8wm-fg4c
CVE: CVE-2023-22602
CWE: CWE-436
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-01-14
Source: https://github.com/advisories/GHSA-7cxr-h8wm-fg4c
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-root` — affected >=0 <1.11.0

## Details
When using Apache Shiro before 1.11.0 together with Spring Boot 2.6+, a specially crafted HTTP request may cause an authentication bypass. The authentication bypass occurs when Shiro and Spring Boot are using different pattern-matching techniques. Both Shiro and Spring Boot < 2.6 default to Ant style pattern matching. Mitigation: Update to Apache Shiro 1.11.0, or set the following Spring Boot configuration value: `spring.mvc.pathmatch.matching-strategy = ant_path_matcher`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22602
- https://github.com/apache/shiro
- https://lists.apache.org/thread/dzj0k2smpzzgj6g666hrbrgsrlf9yhkl
