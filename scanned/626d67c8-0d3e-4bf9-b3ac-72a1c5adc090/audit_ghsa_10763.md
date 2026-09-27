# [M] Spring AI Vulnerable to OOM by attacker-controlled PDF

## Summary
Severity: Medium
Advisory: GHSA-26gg-9gv2-v27j
CVE: CVE-2026-40980
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-26gg-9gv2-v27j
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-pdf-document-reader` — affected >=1.0.0 <1.0.6
- Maven: `org.springframework.ai:spring-ai-pdf-document-reader` — affected >=1.1.0 <1.1.5

## Details
In Spring AI, a malicious PDF file can be crafted that triggers the allocation of unreasonable amounts of memory when handled by `ForkPDFLayoutTextStripper`.

Affected versions:
Spring AI: 1.0.0 - 1.0.5 (fixed in 1.0.6), 1.1.0 - 1.1.4 (fixed in 1.1.5)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40980
- https://github.com/spring-projects/spring-ai
- https://spring.io/security/cve-2026-40980
