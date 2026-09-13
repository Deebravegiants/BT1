# [H] NATS Server: Route API Auth Bypass

## Summary
Severity: High
Advisory: BIT-nats-2026-58253
Aliases: CVE-2026-58253, GHSA-38x3-76xf-cq45
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-nats-2026-58253
Type: osv

## Affected
- Bitnami: `nats` — affected >=2.12.0 <2.12.6

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.0, 2.12.7, and 2.11.16, when no_auth_user was configured, a parser fast path intended for ordinary client connections could also apply to route or leafnode listeners, allowing an unauthenticated peer to bypass inter-server CONNECT authentication and operate with the privileges associated with that connection type. This issue is fixed in versions 2.14.0, 2.12.7, and 2.11.16.

## References
- https://github.com/nats-io/nats-server/commit/7b81dd455ea95960090a84858c7662827948d1b6
- https://github.com/nats-io/nats-server/commit/8b8e1ad4ceed32321e00d4fc6e76be05bc13bca6
- https://github.com/nats-io/nats-server/commit/b86147e81710a52b72a7f7275f91d69f723f5cb3
- https://github.com/nats-io/nats-server/releases/tag/v2.11.16
- https://github.com/nats-io/nats-server/releases/tag/v2.12.7
- https://github.com/nats-io/nats-server/releases/tag/v2.14.0
- https://github.com/nats-io/nats-server/security/advisories/GHSA-38x3-76xf-cq45
- https://nvd.nist.gov/vuln/detail/CVE-2026-58253
