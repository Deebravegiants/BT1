# [C] DevGuard has an unauthenticated identity assertion via `X-Admin-Token` header

## Summary
Severity: Critical
Advisory: GHSA-2g9v-7mr5-fgjg
CVE: CVE-2026-42300
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-2g9v-7mr5-fgjg
Type: github-advisory

## Affected
- Go: `github.com/l3montree-dev/devguard` — affected >=0 <1.2.2

## Details
### Impact
The `SessionMiddleware` accepts a client-supplied `X-Admin-Token` HTTP request header and uses its raw string value as the authenticated `userID` when no Kratos session cookie is present. An unauthenticated attacker who knows or can guess a target user's Kratos identity UUID can issue requests as that user. Where the target user is an organisation `admin` or `owner`, this gives the attacker full control over that organisation's DevGuard resources.

### Patches
The release v1.2.2 patches this issue. Update your DevGuard API Instances to this version.

### Workarounds
Configure a reverse proxy to strip the `X-Admin-Token` header before sending requests to the DevGuard API.

### Resources
Fixed commit: https://github.com/l3montree-dev/devguard/commit/6f38310bf93b2a63df3055038f4da82b1f4e6d9a

## References
- https://github.com/l3montree-dev/devguard/security/advisories/GHSA-2g9v-7mr5-fgjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-42300
- https://github.com/l3montree-dev/devguard/commit/6f38310bf93b2a63df3055038f4da82b1f4e6d9a
- https://github.com/l3montree-dev/devguard
