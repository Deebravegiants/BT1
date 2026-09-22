# [H] Spring AI has a VectorStore FilterExpression Converter injection

## Summary
Severity: High
Advisory: GHSA-qc4j-qjqx-vr58
CVE: CVE-2026-40967
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-qc4j-qjqx-vr58
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-vector-store` — affected >=1.0.0 <1.0.6
- Maven: `org.springframework.ai:spring-ai-vector-store` — affected >=1.1.0 <1.1.5

## Details
In Spring AI, various FilterExpressionConverter implementations accept a filter expression object and translate them to specific vector store query languages. In several cases, keys and values are not properly escaped, leading to the ability to alter the query.

Affected versions:
Spring AI: 1.0.0 - 1.0.5 (fixed in 1.0.6), 1.1.0 - 1.1.4 (fixed in 1.1.5)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40967
- https://github.com/spring-projects/spring-ai
- https://spring.io/security/cve-2026-40967
