# [M] Spring AI's support for Anthropic's Skills API used LLM-influenced filenames unsanitized in Path.resolve before writing files to disk

## Summary
Severity: Medium
Advisory: GHSA-cc4m-mp48-x7qg
CVE: CVE-2026-41863
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-cc4m-mp48-x7qg
Type: github-advisory

## Affected
- Maven: `org.springframework.ai:spring-ai-anthropic` — affected >=1.1.0 <1.1.7

## Details
Spring AI's support for Anthropic's Skills API used LLM-influenced filenames unsanitized in Path.resolve before writing files to disk. This could allow a malicious user to write files outside the intended target directory, including restricted directories.

Affected versions:
Spring AI: 1.1.0 through 1.1.7

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41863
- https://github.com/spring-projects/spring-ai
- https://spring.io/security/cve-2026-41863
