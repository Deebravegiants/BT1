# [M] JLSEC-2026-1129

## Summary
Severity: Medium
Advisory: JLSEC-2026-1129
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1129
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.15 and 2.12.6, the NATS message header `Nats-Request-Info:` is supposed to be a guarantee of identity by the NATS server, but the stripping of this header from inbound messages was not fully effective. An attacker with valid credentials for any regular client interface could thus spoof their identity to services which rely upon this header. Versions 2.11.15 and 2.12.6 contain a fix. No known workarounds are available.

## References
- https://advisories.nats.io/CVE/secnote-2026-09.txt
- https://github.com/nats-io/nats-server/security/advisories/GHSA-pwx7-fx9r-hr4h
