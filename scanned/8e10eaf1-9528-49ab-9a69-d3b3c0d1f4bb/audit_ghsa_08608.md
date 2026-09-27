# [H] Spring AI: ChatMemory DEFAULT_CONVERSATION_ID causes unintended cross-user data leakage

## Summary
Severity: High
Advisory: GHSA-q62f-h9x2-gcqc
CVE: CVE-2026-41712
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-q62f-h9x2-gcqc
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-client-chat` — affected >=0 <1.0.7
- Maven: `org.springframework.ai:spring-ai-client-chat` — affected >=1.1.0-M1 <1.1.6
- Maven: `org.springframework.ai:spring-ai-client-chat` — affected >=2.0.0-M1 <2.0.0-M6
- Maven: `org.springframework.ai:spring-ai-model` — affected >=0 <1.0.7
- Maven: `org.springframework.ai:spring-ai-model` — affected >=1.1.0-M1 <1.1.6
- Maven: `org.springframework.ai:spring-ai-model` — affected >=2.0.0-M1 <2.0.0-M6
- Maven: `org.springframework.ai:spring-ai-advisors-vector-store` — affected >=0 <1.0.7
- Maven: `org.springframework.ai:spring-ai-advisors-vector-store` — affected >=1.1.0-M1 <1.1.6
- Maven: `org.springframework.ai:spring-ai-advisors-vector-store` — affected >=2.0.0-M1 <2.0.0-M6

## Details
Spring AI's chat memory component contained a problematic default that, when not explicitly overridden, could result in unintended data exposure between users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41712
- https://github.com/spring-projects/spring-ai/commit/59ab7521f0a8f67c89359e910a20472d572b4dd9
- https://spring.io/security/cve-2026-41712
