# [M] OpenClaw: Forwarding header spoofing bypasses gateway.trustedProxies origin detection

## Summary
Severity: Medium
Advisory: GHSA-844j-xrrq-wgh4
CVE: CVE-2026-35656
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-844j-xrrq-wgh4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
When gateway.trustedProxies was configured, spoofed loopback hops in forwarding headers could be accepted as the client origin and weaken downstream auth and rate-limit decisions.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `fc2d29ea926f47c428c556e92ec981441228d2a4`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- src/gateway/net.ts now ignores loopback forwarded hops before trusted-proxy client resolution.
- That shipped origin fix is the one consumed by canvas auth and gateway auth-rate-limit paths that rely on resolved client identity.

OpenClaw thanks @lintsinghua for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-844j-xrrq-wgh4
- https://nvd.nist.gov/vuln/detail/CVE-2026-35656
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/fc2d29ea926f47c428c556e92ec981441228d2a4
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-xff-loopback-spoofing-bypass-in-canvas-authentication-and-rate-limiter
