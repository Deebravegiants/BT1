# [C] Spring AI: SpEL injection is triggered when a user-supplied value is used as a filter expression key

## Summary
Severity: Critical
Advisory: GHSA-fvh3-672c-7p6c
CVE: CVE-2026-22738
CWE: CWE-88, CWE-917, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-fvh3-672c-7p6c
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-vector-store` — affected >=1.0.0 <1.0.5
- Maven: `org.springframework.ai:spring-ai-vector-store` — affected >=1.1.0-M1 <1.1.4

## Details
In Spring AI, a SpEL injection vulnerability exists in SimpleVectorStore when a user-supplied value is used as a filter expression key. A malicious actor could exploit this to execute arbitrary code. Only applications that use SimpleVectorStore and pass user-supplied input as a filter expression key are affected.

This issue affects Spring AI: from 1.0.0 before 1.0.5, from 1.1.0 before 1.1.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22738
- https://github.com/spring-projects/spring-ai/commit/ba9220b22383e430d5f801ce8e4fa01cf9e75f29
- https://github.com/spring-projects/spring-ai
- https://github.com/spring-projects/spring-ai/releases/tag/v1.0.5
- https://github.com/spring-projects/spring-ai/releases/tag/v1.1.4
- https://spring.io/security/cve-2026-22738
