# [M] JLSEC-2026-1130

## Summary
Severity: Medium
Advisory: JLSEC-2026-1130
Ecosystem: Julia
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1130
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. The nats-server offers a `Nats-Request-Info:` message header, providing information about a request. This is supposed to provide enough information to allow for account/user identification, such that NATS clients could make their own decisions on how to trust a message, provided that they trust the nats-server as a broker. A leafnode connecting to a nats-server is not fully trusted unless the system account is bridged too. Thus identity claims should not have propagated unchecked. Prior to versions 2.11.15 and 2.12.6, NATS clients relying upon the Nats-Request-Info: header could be spoofed. This does not directly affect the nats-server itself, but the CVSS Confidentiality and Integrity scores are based upon what a hypothetical client might choose to do with this NATS header. Versions 2.11.15 and 2.12.6 contain a fix. No known workarounds are available.

## References
- https://advisories.nats.io/CVE/secnote-2026-08.txt
- https://github.com/nats-io/nats-server/security/advisories/GHSA-55h8-8g96-x4hj
