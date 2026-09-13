# [M] Spring AI's VectorStoreChatMemoryAdvisor conversation scoping can lead to cross-tenant memory exfiltration

## Summary
Severity: Medium
Advisory: GHSA-v6x6-pjxw-3pv2
CVE: CVE-2026-40966
CWE: CWE-284
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-v6x6-pjxw-3pv2
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-advisors-vector-store` — affected >=1.0.0 <1.0.6
- Maven: `org.springframework.ai:spring-ai-advisors-vector-store` — affected >=1.1.0 <1.1.5

## Details
In Spring AI, an attacker can bypass conversation isolation and exfiltrate sensitive memory from other users’ chat histories, including secrets and credentials, by injecting filter logic through conversationId. Only applications that use VectorStoreChatMemoryAdvisor and pass user-supplied input as a conversationId are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40966
- https://github.com/spring-projects/spring-ai
- https://jinyeong.seol.pro/blogs/cve-2026-40966/en
- https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?version=3.1&vector=AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N
- https://spring.io/security/cve-2026-40966
