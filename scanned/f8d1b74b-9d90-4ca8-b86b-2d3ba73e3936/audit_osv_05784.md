# [H] BIT-guacamole-2023-30575

## Summary
Severity: High
Advisory: BIT-guacamole-2023-30575
Aliases: BIT-guacamole-server-2023-30575, CVE-2023-30575
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-guacamole-2023-30575
Type: osv

## Affected
- Bitnami: `guacamole` — affected >=0 <1.5.2

## Details
Apache Guacamole 1.5.1 and older may incorrectly calculate the lengths of instruction elements sent during the Guacamole protocol handshake, potentially allowing an attacker to inject Guacamole instructions during the handshake through specially-crafted data.

## References
- https://lists.apache.org/thread/tn63n2lon0h5p45oft834t1dqvvxownv
