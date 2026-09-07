# [M] Flowise: Weak Default JWT Secrets

## Summary
Severity: Medium
Advisory: GHSA-cc4f-hjpj-g9p8
CWE: CWE-327
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-cc4f-hjpj-g9p8
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
**Detection Method:** Kolega.dev Deep Code Scan

| Attribute | Value |
|---|---|
| Severity | Critical |
| Location | packages/server/src/enterprise/middleware/passport/index.ts:29-34 |
| Practical Exploitability | High |
| Developer Approver | faizan@kolega.ai |

### Description
JWT secrets have weak hardcoded defaults ('auth_token', 'refresh_token', 'AUDIENCE', 'ISSUER'). Attackers can forge valid JWTs and impersonate any user.

### Affected Code
```
const jwtAudience = process.env.JWT_AUDIENCE || 'AUDIENCE'
const jwtIssuer = process.env.JWT_ISSUER || 'ISSUER'
const jwtAuthTokenSecret = process.env.JWT_AUTH_TOKEN_SECRET || 'auth_token'
const jwtRefreshSecret = process.env.JWT_REFRESH_TOKEN_SECRET || process.env.JWT_AUTH_TOKEN_SECRET || 'refresh_token'
```

### Evidence
All JWT defaults are weak strings. Refresh token falls back to auth token which is a design flaw. If any environment variable is unset, weak default is used.

### Impact
Complete authentication bypass. Attackers can forge valid JWTs for any user account. No authentication required to access protected endpoints. Can escalate to admin access.

### Recommendation
Remove all default secrets - require all JWT environment variables to be explicitly set. Add startup validation throwing error if any JWT secret is missing. Use cryptographically random secrets (256+ bits) for each secret independently. Implement JWT secret rotation mechanism.

### Notes
The JWT secrets have genuinely weak hardcoded defaults ('auth_token', 'refresh_token', 'AUDIENCE', 'ISSUER') at lines 29-34. If an administrator deploys without setting the environment variables JWT_AUTH_TOKEN_SECRET, JWT_REFRESH_TOKEN_SECRET, JWT_AUDIENCE, and JWT_ISSUER, the application will use these trivially guessable values. An attacker knowing these defaults (which are publicly visible in the source code) can forge valid JWTs to impersonate any user, including administrators. The fallback chain at line 34 where jwtRefreshSecret falls back to jwtAuthTokenSecret is an additional design weakness - if only JWT_AUTH_TOKEN_SECRET is set, both tokens share the same secret. While .env.example files provide placeholder values, these are also weak and publicly visible. The application should fail to start if these secrets are not explicitly configured with strong values, rather than silently falling back to insecure defaults.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-cc4f-hjpj-g9p8
- https://github.com/FlowiseAI/Flowise
