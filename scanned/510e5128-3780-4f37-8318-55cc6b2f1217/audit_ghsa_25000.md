# [C] Remote code execution in PATCH requests in Spring Data REST

## Summary
Severity: Critical
Advisory: GHSA-9qf9-28h9-hqcj
CVE: CVE-2017-8046
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-9qf9-28h9-hqcj
Type: github-advisory

## Affected
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=0 <2.6.9.RELEASE
- Maven: `org.springframework.data:spring-data-rest-core` — affected >=3.0.0 <3.0.1.RELEASE

## Details
Malicious PATCH requests submitted to servers using Spring Data REST versions prior to 2.6.9 (Ingalls SR9), versions prior to 3.0.1 (Kay SR1) can use specially crafted JSON data to run arbitrary Java code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8046
- https://github.com/spring-projects/spring-data-rest/issues/1487
- https://github.com/spring-projects/spring-data-rest/issues/1520
- https://access.redhat.com/errata/RHSA-2018:2405
- https://bugzilla.redhat.com/show_bug.cgi?id=1553024
- https://github.com/spring-projects/spring-data-rest
- https://jira.spring.io/browse/DATAREST-1127?redirect=false
- https://pivotal.io/security/cve-2017-8046
