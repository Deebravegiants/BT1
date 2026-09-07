# [M] OpenClaw: BlueBubbles beta plugin webhook auth hardening (remove passwordless fallback)

## Summary
Severity: Medium
Advisory: GHSA-5mx2-2mgw-x8rm
CVE: CVE-2026-32896
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-5mx2-2mgw-x8rm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
### Summary
BlueBubbles webhook auth in the optional beta iMessage plugin allowed a passwordless fallback path. In some reverse-proxy/local routing setups, this could allow unauthenticated webhook events.

### Affected Component and Scope
- Component: `extensions/bluebubbles` webhook handler
- Scope: only deployments using the optional BlueBubbles plugin where webhook password auth was not configured for incoming webhook events

### Affected Packages / Versions
- Package: `openclaw/openclaw` (npm)
- Latest published npm version at triage time (2026-02-21): `2026.2.19-2`
- Affected structured range: `<=2026.2.19-2`
- Fixed on `main`; planned patched release: `2026.2.21` (`>=2026.2.21`)

### Details
The vulnerable implementation had multiple auth branches, including a passwordless fallback with loopback/proxy heuristics.

The fix now uses one authentication codepath:
- inbound webhook token/guid must match `channels.bluebubbles.password`
- webhook target matching is consolidated to shared plugin-sdk logic
- BlueBubbles config validation now requires `password` when `serverUrl` is set

### Impact
BlueBubbles is an optional beta iMessage plugin, and onboarding/channel-add flows already require a password. Practical exposure is mainly custom/manual configurations that omitted webhook password authentication.

### Remediation
- Upgrade to a release that includes this patch (`>=2026.2.21`, planned).
- Ensure BlueBubbles webhook delivery includes a matching password (`?password=<password>` or `x-password`).

### Fix Commit(s)
- `6b2f2811dc623e5faaf2f76afaa9279637174590`
- `283029bdea23164ab7482b320cb420d1b90df806`

### Release Process Note
`patched_versions` is pre-set to the planned next release (`2026.2.21`) so once npm release is out, advisory publish can proceed without additional ticket edits.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5mx2-2mgw-x8rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32896
- https://github.com/openclaw/openclaw/commit/283029bdea23164ab7482b320cb420d1b90df806
- https://github.com/openclaw/openclaw/commit/6b2f2811dc623e5faaf2f76afaa9279637174590
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthenticated-webhook-access-via-passwordless-fallback-in-bluebubbles-plugin
