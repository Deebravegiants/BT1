# [H] JSONPath Injection in Spring AI Vector Stores FilterExpressionConverter

## Summary
Severity: High
Advisory: GHSA-rp9g-qx29-88cp
CVE: CVE-2026-22729
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-rp9g-qx29-88cp
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-vector-store` — affected >=1.1.0-M1 <1.1.3
- Maven: `org.springframework.ai:spring-ai-vector-store` — affected >=0 <1.0.4

## Details
A JSONPath injection vulnerability in Spring AI's AbstractFilterExpressionConverter allows authenticated users to bypass metadata-based access controls through crafted filter expressions. User-controlled input passed to FilterExpressionBuilder is concatenated into JSONPath queries without proper escaping, enabling attackers to inject arbitrary JSONPath logic and access unauthorized documents.

This vulnerability affects applications using vector stores that extend AbstractFilterExpressionConverter for multi-tenant isolation, role-based access control, or document filtering based on metadata.

The vulnerability occurs when user-supplied values in filter expressions are not escaped before being inserted into JSONPath queries. Special characters like ", ||, and && are passed through unescaped, allowing injection of arbitrary JSONPath logic that can alter the intended query semantics.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22729
- https://github.com/spring-projects/spring-ai
- https://github.com/spring-projects/spring-ai/releases/tag/v1.0.4
- https://github.com/spring-projects/spring-ai/releases/tag/v1.1.3
- https://spring.io/security/cve-2026-22729
