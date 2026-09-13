# [H] BIT-guacamole-2023-30576

## Summary
Severity: High
Advisory: BIT-guacamole-2023-30576
Aliases: BIT-guacamole-server-2023-30576, CVE-2023-30576
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-guacamole-2023-30576
Type: osv

## Affected
- Bitnami: `guacamole` — affected >=0.9.0 <1.5.2

## Details
Apache Guacamole 0.9.10 through 1.5.1 may continue to reference a freed RDP audio input buffer. Depending on timing, this may allow an attacker to execute arbitrary code with the privileges of the guacd process.

## References
- https://lists.apache.org/thread/vgtvxb3w7mm84hx6v8dfc0onsoz05gb6
