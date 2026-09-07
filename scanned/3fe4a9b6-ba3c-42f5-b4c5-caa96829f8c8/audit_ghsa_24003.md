# [M] Spring Batch Admin vulnerable to Stored Cross-site scripting (XSS) in the file upload functionality

## Summary
Severity: Medium
Advisory: GHSA-49mj-77q5-qw5g
CVE: CVE-2017-12882
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-49mj-77q5-qw5g
Type: github-advisory

## Affected
- Maven: `org.springframework.batch:spring-batch-admin-manager` — affected >=0 <1.3.0.RELEASE

## Details
Stored Cross-site scripting (XSS) vulnerability in Spring Batch Admin before 1.3.0 allows remote authenticated users to inject arbitrary JavaScript or HTML via the file upload functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12882
- https://github.com/spring-attic/spring-batch-admin
- http://www.openwall.com/lists/oss-security/2017/08/16/5
