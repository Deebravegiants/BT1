# [H] OpenClaw has encoded-path auth bypass in plugin `/api/channels` route classification

## Summary
Severity: High
Advisory: GHSA-v865-p3gq-hw6m
CVE: CVE-2026-32004
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-v865-p3gq-hw6m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.2

## Details
### Summary (Updated March 2, 2026)
Encoded alternate-path requests could bypass plugin route auth checks for `/api/channels/*` due to canonicalization depth mismatch in vulnerable builds.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published vulnerable version: `2026.3.1`
- Affected range: `<= 2026.3.1`
- Patched release: `2026.3.2` (`patched_versions: >= 2026.3.2`)

### Technical Details
In affected versions, plugin auth-path classification and route-path canonicalization could diverge for deeply encoded slash variants (for example multi-encoded `%2f`). That mismatch allowed alternate encoded paths to evade protected-prefix auth checks while still resolving to `/api/channels/...` in plugin route handling.

The fix set hardens this class of issue by:
- canonicalizing route paths to a bounded fixpoint,
- failing closed on malformed or unresolved canonicalization depth,
- requiring explicit plugin-route auth contracts (no implicit auth default),
- enforcing route ownership/conflict guards for duplicate route registrations, and
- using shared webhook route lifecycle registration to avoid stale/conflicting route surfaces.

### Affected Deployments
Deployments exposing plugin HTTP routes and relying on gateway auth for `/api/channels/*` protection.

### Fix Commit(s)
- `93b07240257919f770d1e263e1f22753937b80ea`
- `2fd8264ab03bd178e62a5f0c50d1c8556c17f12d`
- `d74bc257d8432f17e50b23ae713d7e0623a1fe0f`
- `7a7eee920a176a0043398c6b37bf4cc6eb983eeb`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v865-p3gq-hw6m
- https://nvd.nist.gov/vuln/detail/CVE-2026-32004
- https://github.com/openclaw/openclaw/commit/2fd8264ab03bd178e62a5f0c50d1c8556c17f12d
- https://github.com/openclaw/openclaw/commit/7a7eee920a176a0043398c6b37bf4cc6eb983eeb
- https://github.com/openclaw/openclaw/commit/93b07240257919f770d1e263e1f22753937b80ea
- https://github.com/openclaw/openclaw/commit/d74bc257d8432f17e50b23ae713d7e0623a1fe0f
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-encoded-path-in-api-channels-route
