# [H] OpenClaw Gateway tool allowed unrestricted gatewayUrl override

## Summary
Severity: High
Advisory: GHSA-g6q9-8fvw-f7rf
CVE: CVE-2026-26322
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-g6q9-8fvw-f7rf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
## Summary
The Gateway tool accepted a tool-supplied `gatewayUrl` without sufficient restrictions, which could cause the OpenClaw host to attempt outbound WebSocket connections to user-specified targets.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.13`
- Patched versions: `>= 2026.2.14` (planned)

## What Is Needed To Trigger This
This requires the ability to invoke tools that accept `gatewayUrl` overrides (directly or indirectly). In typical setups this is limited to authenticated operators, trusted automation, or environments where tool calls are exposed to non-operators.

In other words, this is not a drive-by issue for arbitrary internet users unless a deployment explicitly allows untrusted users to trigger these tool calls.

## Details
Some tool call paths allowed `gatewayUrl` overrides to flow into the Gateway WebSocket client without validation or allowlisting. This meant the host could be instructed to attempt connections to non-gateway endpoints (for example, localhost services, private network addresses, or cloud metadata IPs).

## Impact
In the common case, this results in an outbound connection attempt from the OpenClaw host (and corresponding errors/timeouts). In environments where the tool caller can observe the results, this can also be used for limited network reachability probing. If the target speaks WebSocket and is reachable, further interaction may be possible.

## Fix
Tool-supplied `gatewayUrl` overrides are now restricted to loopback (on the configured gateway port) or the configured `gateway.remote.url`. Disallowed protocols, credentials, query/hash, and non-root paths are rejected.

## Fix Commit(s)
- c5406e1d2434be2ef6eb4d26d8f1798d718713f4

## Release Process Note
`patched_versions` is set to the planned next release. Once the npm release is published, the advisory can be published without further edits.

Thanks @p80n-sec for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g6q9-8fvw-f7rf
- https://nvd.nist.gov/vuln/detail/CVE-2026-26322
- https://github.com/openclaw/openclaw/commit/c5406e1d2434be2ef6eb4d26d8f1798d718713f4
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
