# [H] Spring AI: Prompt Injection via Memory Poisoning in PromptChatMemoryAdvisor

## Summary
Severity: High
Advisory: GHSA-5852-phmh-8fhr
CVE: CVE-2026-41713
CWE: CWE-1336
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-5852-phmh-8fhr
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-client-chat` — affected >=0 <1.0.7
- Maven: `org.springframework.ai:spring-ai-client-chat` — affected >=1.1.0-M1 <1.1.6

## Details
A malicious user could craft input that is stored in conversation memory and later interpreted by the model in an unintended way. Applications using the affected advisor with user-controlled input may be susceptible to manipulation of model behavior across conversation turns.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41713
- https://github.com/spring-projects/spring-ai
- https://spring.io/security/cve-2026-41713
