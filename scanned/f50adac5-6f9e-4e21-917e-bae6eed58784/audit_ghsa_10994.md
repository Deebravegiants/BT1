# [M] OpenClaw: /api/channels gateway-auth boundary bypass via path canonicalization mismatch

## Summary
Severity: Medium
Advisory: GHSA-8j2w-6fmm-m587
CVE: CVE-2026-32031
CWE: CWE-288
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-8j2w-6fmm-m587
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.26

## Details
### Summary
Gateway auth for plugin channel endpoints can be bypassed when path canonicalization differs between the gateway guard and plugin handler routing.

### Details
On affected versions, `server-http` only applies gateway auth when raw `requestPath` matches exactly:
- `/api/channels`
- `/api/channels/*`

If a plugin handler canonicalizes path input (for example `decodeURIComponent(pathname).toLowerCase()`), requests like:
- `/API/channels/nostr/default/profile`
- `/api/channels%2Fnostr%2Fdefault%2Fprofile`
can be interpreted as `/api/channels/*` by the plugin, while the gateway auth guard is skipped.

### Impact
Authentication boundary bypass for plugin channel HTTP routes under canonicalization mismatch conditions. Unauthorized callers may access plugin channel APIs that are expected to require gateway auth.

CWE: CWE-288 (Authentication Bypass Using an Alternate Path or Channel)
CVSS: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N` (Base 5.3, Moderate)

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8j2w-6fmm-m587
- https://nvd.nist.gov/vuln/detail/CVE-2026-32031
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authentication-bypass-via-path-canonicalization-mismatch-in-api-channels-gateway
