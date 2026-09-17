# [M] Tinyauth's OIDC authorization codes are not bound to client on token exchange

## Summary
Severity: Medium
Advisory: GHSA-xg2q-62g2-cvcm
CVE: CVE-2026-32245
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-xg2q-62g2-cvcm
Type: github-advisory

## Affected
- Go: `github.com/steveiliop56/tinyauth` — affected >=0 <1.0.1-20260311144920-9eb2d33064b7

## Details
### Summary

The OIDC token endpoint does not verify that the client exchanging an authorization code is the same client the code was issued to. A malicious OIDC client operator can exchange another client's authorization code using their own client credentials, obtaining tokens for users who never authorized their application. This violates RFC 6749 Section 4.1.3.

### Details

When an authorization code is created, `StoreCode` at `internal/service/oidc_service.go:305-322` correctly stores the `ClientID` alongside the code hash in the database (line 316).

During token exchange at `internal/controller/oidc_controller.go:267-309`, the handler retrieves the code entry at line 268 and validates the `redirect_uri` at line 291, but never compares `entry.ClientID` against the requesting client's ID (`creds.ClientID`). The code proceeds directly to `GenerateAccessToken` at line 299.

The developers clearly intended this check to exist, the refresh token flow at `internal/service/oidc_service.go:508-510` has the exact guard: `if entry.ClientID != reqClientId { return TokenResponse{}, ErrInvalidClient }`. It was simply omitted from the authorization code grant.

The `entry.ClientID` field is stored in the database but never read during authorization code exchange.

### PoC

Prerequisites: a tinyauth instance with two OIDC clients configured (Client A and Client B). Both clients must have at least one overlapping redirect URI, or the attacker must be able to intercept the authorization code from Client A's redirect (via referrer leak, browser history, log access, etc.).

Step 1 — Log in as a normal user:

```
curl -c cookies.txt -X POST http://localhost:3000/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Step 2 — Authorize with Client A:

```
curl -b cookies.txt -X POST http://localhost:3000/api/oidc/authorize \
  -H "Content-Type: application/json" \
  -d '{"client_id":"client-a-id","redirect_uri":"http://localhost:8080/callback","response_type":"code","scope":"openid","state":"test"}'
```

Extract the `code` parameter from the `redirect_uri` in the response.

Step 3 — Exchange Client A's code using Client B's credentials:

```
curl -X POST http://localhost:3000/api/oidc/token \
  -u "client-b-id:client-b-secret" \
  -d "grant_type=authorization_code&code=<CODE_FROM_STEP_2>&redirect_uri=http://localhost:8080/callback"
```

The server returns a valid `access_token`, `id_token`, and `refresh_token`. Client B has obtained tokens for a user who only authorized Client A.

### Impact

A malicious OIDC relying party operator who can intercept or observe an authorization code issued to a different client can exchange it for tokens under their own client identity. This enables user impersonation across OIDC clients on the same tinyauth instance. The attack requires a multi-client deployment and a way to obtain the victim client's authorization code (which is passed as a URL query parameter and can leak through referrer headers, browser history, or server logs). Single-client deployments are not affected.

## References
- https://github.com/steveiliop56/tinyauth/security/advisories/GHSA-xg2q-62g2-cvcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-32245
- https://github.com/steveiliop56/tinyauth/commit/b2a1bfb1f532e87f205fa3afa3fc9f148c53ab89
- https://github.com/steveiliop56/tinyauth
- https://github.com/steveiliop56/tinyauth/releases/tag/v5.0.3
- https://pkg.go.dev/vuln/GO-2026-4689
