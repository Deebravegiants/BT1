# [H] Trigger.dev: Cross-tenant object read/write via path traversal in packet presign API

## Summary
Severity: High
Advisory: CVE-2026-73659
Aliases: GHSA-m3mf-37q7-8928
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73659
Type: osv

## Details
Trigger.dev is the open-source platform for building AI workflows in TypeScript. From 4.4.2 until 4.5.0, the packet presign routes in apps/webapp/app/routes/api.v1.packets.$.ts pass a caller-controlled filename through resolveStoreProtocolForPacketPresign to generatePresignedUrl and generatePresignedRequest in apps/webapp/app/v3/objectStore.server.ts, allowing .. traversal to escape the packets/<projectRef>/<env>/ object-store prefix and enabling a project API key to read or overwrite another organization's offloaded task payloads and outputs on multi-organization self-hosted instances. This issue is fixed in version 4.5.0.

## References
- https://github.com/triggerdotdev/trigger.dev/releases/tag/v4.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73659.json
- https://github.com/triggerdotdev/trigger.dev/security/advisories/GHSA-m3mf-37q7-8928
- https://nvd.nist.gov/vuln/detail/CVE-2026-73659
- https://github.com/triggerdotdev/trigger.dev/commit/db4074df54db06b0656becf3f974345c90fa202e
- https://github.com/triggerdotdev/trigger.dev/pull/3830
