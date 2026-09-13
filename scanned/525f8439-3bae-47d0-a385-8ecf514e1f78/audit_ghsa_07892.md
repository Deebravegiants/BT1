# [H] OpenClaw BlueBubbles webhook auth bypass via loopback proxy trust

## Summary
Severity: High
Advisory: GHSA-pchc-86f6-8758
CVE: CVE-2026-26316
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-pchc-86f6-8758
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.13
- npm: `@openclaw/bluebubbles` — affected >=0 <2026.2.13

## Details
### Summary

In affected versions, the optional BlueBubbles iMessage channel plugin could accept webhook requests as authenticated based only on the TCP peer address being loopback (`127.0.0.1`, `::1`, `::ffff:127.0.0.1`) even when the configured webhook secret was missing or incorrect. This does not affect the default iMessage integration unless BlueBubbles is installed and enabled.

### Affected Packages / Versions

- npm: `openclaw` `< 2026.2.13`
- npm: `@openclaw/bluebubbles` `< 2026.2.13`

### Details

If a deployment exposes the BlueBubbles webhook endpoint through a same-host reverse proxy (or an attacker can reach loopback via SSRF), an unauthenticated party may be able to inject inbound webhook events into the agent pipeline.

### Fix Commit(s)

- f836c385ffc746cb954e8ee409f99d079bfdcd2f
- 743f4b28495cdeb0d5bf76f6ebf4af01f6a02e5a (defense-in-depth)

### Mitigations

- Set a non-empty BlueBubbles webhook password.
- Avoid deployments where a public-facing reverse proxy forwards to a loopback-bound Gateway without strong upstream authentication.

Thanks @MegaManSec (https://joshua.hu) of [AISLE Research Team](https://aisle.com/) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-pchc-86f6-8758
- https://nvd.nist.gov/vuln/detail/CVE-2026-26316
- https://github.com/openclaw/openclaw/commit/743f4b28495cdeb0d5bf76f6ebf4af01f6a02e5a
- https://github.com/openclaw/openclaw/commit/f836c385ffc746cb954e8ee409f99d079bfdcd2f
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.12
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.13
