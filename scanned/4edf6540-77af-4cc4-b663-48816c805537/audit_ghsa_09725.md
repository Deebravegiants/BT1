# [M] Flowise: Weak Default Express Session Secret

## Summary
Severity: Medium
Advisory: GHSA-2qqc-p94c-hxwh
CWE: CWE-798
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-2qqc-p94c-hxwh
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
**Detection Method:** Kolega.dev Deep Code Scan

| Attribute | Value |
|---|---|
| Location | packages/server/src/enterprise/middleware/passport/index.ts:55 |
| Practical Exploitability | High |
| Developer Approver | faizan@kolega.ai |

### Description
Express session secret has a weak default value 'flowise' when EXPRESS_SESSION_SECRET is not set.

### Affected Code
```
secret: process.env.EXPRESS_SESSION_SECRET || 'flowise'
```

### Evidence
The default session secret 'flowise' is publicly visible and weak. Session cookies signed with this secret can be forged by attackers.

### Impact
Session hijacking and forgery - attackers can create arbitrary session cookies to impersonate any user, bypassing all authentication mechanisms.

### Recommendation
Require EXPRESS_SESSION_SECRET to be set with a strong random value. Throw an error on startup if not configured. Use cryptographically strong random strings (minimum 256 bits).

### Notes
The Express session secret defaults to the string 'flowise' when EXPRESS_SESSION_SECRET is not set (line 55). This secret is used to sign session cookies via express-session middleware. Since 'flowise' is publicly visible in the source code, an attacker can forge valid session cookies to impersonate any user without authentication. The .env.example file has this commented out (# EXPRESS_SESSION_SECRET=flowise), implying it's optional, which compounds the risk. Unlike development-only defaults, this code path is active in production if the environment variable is not set. The application should require EXPRESS_SESSION_SECRET to be explicitly configured with a cryptographically strong random value and fail to start otherwise.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-2qqc-p94c-hxwh
- https://github.com/FlowiseAI/Flowise
