# [H] JLSEC-2026-1153

## Summary
Severity: High
Advisory: JLSEC-2026-1153
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:L)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1153
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.0, 2.12.7, and 2.11.16, when `no_auth_user` was configured, a parser fast path intended for ordinary client connections could also apply to route or leafnode listeners, allowing an unauthenticated peer to bypass inter-server CONNECT authentication and operate with the privileges associated with that connection type. This issue is fixed in versions 2.14.0, 2.12.7, and 2.11.16.

## References
- https://github.com/nats-io/nats-server/commit/7b81dd455ea95960090a84858c7662827948d1b6
- https://github.com/nats-io/nats-server/commit/8b8e1ad4ceed32321e00d4fc6e76be05bc13bca6
- https://github.com/nats-io/nats-server/commit/b86147e81710a52b72a7f7275f91d69f723f5cb3
- https://github.com/nats-io/nats-server/releases/tag/v2.11.16
- https://github.com/nats-io/nats-server/releases/tag/v2.12.7
- https://github.com/nats-io/nats-server/releases/tag/v2.14.0
- https://github.com/nats-io/nats-server/security/advisories/GHSA-38x3-76xf-cq45
