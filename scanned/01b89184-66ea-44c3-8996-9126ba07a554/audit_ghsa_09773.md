# [M] Spring AI's ONNX model cache defaults to world-writable predictable /tmp directory

## Summary
Severity: Medium
Advisory: GHSA-r5hp-3cgj-j6xv
CVE: CVE-2026-40979
CWE: CWE-377
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-r5hp-3cgj-j6xv
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-transformers` — affected >=1.0.0 <1.0.6
- Maven: `org.springframework.ai:spring-ai-transformers` — affected >=1.1.0 <1.1.5

## Details
In Spring AI, having access to a shared environment can expose the ONNX model used by the application.

Affected versions:
Spring AI: 1.0.0 - 1.0.5 (fixed in 1.0.6), 1.1.0 - 1.1.4 (fixed in 1.1.5)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40979
- https://github.com/spring-projects/spring-ai
- https://spring.io/security/cve-2026-40979
