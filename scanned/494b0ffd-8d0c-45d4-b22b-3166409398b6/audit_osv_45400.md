# [M] JLSEC-2026-1123

## Summary
Severity: Medium
Advisory: JLSEC-2026-1123
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1123
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. The nats-server provides an MQTT client interface. Prior to versions 2.11.15 and 2.12.5, Sessions and Messages can by hijacked via MQTT Client ID malfeasance. Versions 2.11.15 and 2.12.5 patch the issue. No known workarounds are available.

## References
- https://advisories.nats.io/CVE/secnote-2026-06.tx
- https://github.com/nats-io/nats-server/security/advisories/GHSA-fcjp-h8cc-6879
