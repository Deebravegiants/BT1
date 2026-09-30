# [H] Spring AI: Insufficient Validation causes SSRF when processing multimodal messages with user-supplied URLs

## Summary
Severity: High
Advisory: GHSA-mhrg-94vw-45c5
CVE: CVE-2026-22742
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-mhrg-94vw-45c5
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-bedrock-converse` — affected >=1.0.0-M5 <1.0.5
- Maven: `org.springframework.ai:spring-ai-bedrock-converse` — affected >=1.1.0-M1 <1.1.4

## Details
Spring AI's spring-ai-bedrock-converse contains a Server-Side Request Forgery (SSRF) vulnerability in BedrockProxyChatModel when processing multimodal messages that include user-supplied media URLs. Insufficient validation of those URLs allows an attacker to induce the server to issue HTTP requests to unintended internal or external destinations.

This issue affects Spring AI: from 1.0.0 before 1.0.5, from 1.1.0 before 1.1.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22742
- https://github.com/spring-projects/spring-ai/commit/a7d3223bc11a010b93fbc40a17fa9b68c52a8118
- https://github.com/spring-projects/spring-ai
- https://github.com/spring-projects/spring-ai/releases/tag/v1.0.5
- https://github.com/spring-projects/spring-ai/releases/tag/v1.1.4
- https://spring.io/security/cve-2026-22742
