# [H] Spring Integration File Support: FTP/SFTP/SMB server can write arbitrary files anywhere on the client filesystem

## Summary
Severity: High
Advisory: GHSA-792x-6vq6-j8r9
CVE: CVE-2026-40987
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-792x-6vq6-j8r9
Type: github-advisory

## Affected
- Maven: `org.springframework.integration:spring-integration-file` — affected >=7.0.0 <7.0.5
- Maven: `org.springframework.integration:spring-integration-file` — affected >=6.5.0 <6.5.9
- Maven: `org.springframework.integration:spring-integration-file` — affected >=6.4.0
- Maven: `org.springframework.integration:spring-integration-file` — affected >=6.3.0
- Maven: `org.springframework.integration:spring-integration-file` — affected >=0

## Details
A malicious or compromised FTP/SFTP/SMB server can write arbitrary files anywhere on the client filesystem (outside the configured local-directory) with attacker-controlled content.

Affected versions:
Spring Integration 7.0.0 through 7.0.4; 6.5.0 through 6.5.8; 6.4.0 through 6.4.11; 6.3.0 through 6.3.14; 5.5.0 through 5.5.20.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-40987
- https://github.com/spring-projects/spring-integration
- https://spring.io/security/cve-2026-40987
