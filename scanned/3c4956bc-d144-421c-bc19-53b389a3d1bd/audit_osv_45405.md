# [M] JLSEC-2026-1128

## Summary
Severity: Medium
Advisory: JLSEC-2026-1128
Ecosystem: Julia
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1128
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.15 and 2.12.6, users with JetStream admin API access to restore one stream could restore to other stream names, impacting data which should have been protected against them. Versions 2.11.15 and 2.12.6 contain a fix. As a workaround, if developers have configured users to have limited JetStream restore permissions, temporarily remove those permissions.

## References
- https://advisories.nats.io/CVE/secnote-2026-12.txt
- https://github.com/nats-io/nats-server/security/advisories/GHSA-9983-vrx2-fg9c
