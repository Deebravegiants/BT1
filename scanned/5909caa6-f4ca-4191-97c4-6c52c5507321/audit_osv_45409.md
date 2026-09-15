# [M] JLSEC-2026-1132

## Summary
Severity: Medium
Advisory: JLSEC-2026-1132
Ecosystem: Julia
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1132
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.15 and 2.12.6, when using mTLS for client identity, with `verify_and_map` to derive a NATS identity from the client certificate's Subject DN, certain patterns of RDN would not be correctly enforced, allowing for authentication bypass. This does require a valid certificate from a CA already trusted for client certificates, and `DN` naming patterns which the NATS maintainers consider highly unlikely. So this is an unlikely attack. Nonetheless, administrators who have been very sophisticated in their `DN` construction patterns might conceivably be impacted. Versions 2.11.15 and 2.12.6 contain a fix. As a workaround, developers should review their CA issuing practices.

## References
- https://advisories.nats.io/CVE/secnote-2026-13.txt
- https://github.com/nats-io/nats-server/security/advisories/GHSA-3f24-pcvm-5jqc
