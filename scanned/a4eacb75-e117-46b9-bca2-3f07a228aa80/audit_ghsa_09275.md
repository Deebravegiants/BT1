# [H] opentelemetry-collector-contrib's azureauthextension Authenticate method does not validate bearer tokens, allowing auth bypass via replay

## Summary
Severity: High
Advisory: GHSA-pjv4-3c63-699f
CVE: CVE-2026-42602
CWE: CWE-208, CWE-287, CWE-290, CWE-294, CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-pjv4-3c63-699f
Type: github-advisory

## Affected
- Go: `github.com/open-telemetry/opentelemetry-collector-contrib/extension/azureauthextension` — affected >=0.124.0

## Details
### Summary

A server-side authentication bypass in `azureauthextension` allows any party who holds a single valid Azure access token for *any scope the collector's configured identity can mint for* to authenticate to any OpenTelemetry receiver that uses `auth: azure_auth`. The extension's `Authenticate` method does not validate incoming bearer tokens as JWTs. Instead, it calls its own configured credential to obtain an access token and compares the client's token to the result with string equality — and the scope for that server-side token request is taken from the client-supplied `Host` header. As a result, a token minted for any Azure resource the service principal has ever been issued a token for (ARM, Graph, Key Vault, Storage, etc.) will authenticate to the collector if the attacker picks a matching `Host`. Tokens are replayable for the full issued lifetime (commonly several hours for managed identity tokens).

Severity: High (CVSS 8.1). See "Threat model" below for the preconditions that inform that score.

### Root cause

The extension implements both `extensionauth.HTTPClient` (outbound: "attach my identity to requests I send") and `extensionauth.Server` (inbound: "validate a credential someone presented to me"). Those two interfaces look symmetric but are not: holding a credential to present says nothing about the ability to validate a credential someone else presents. The outbound path only requires `credential.GetToken()`; the inbound path requires JWT signature verification against the issuer's JWKS, issuer/audience/exp/nbf checks, and an algorithm allowlist — none of which the extension does.

PR #39178 ("Implement extensionauth.HTTPClient and extensionauth.Server interface functions") added the `Server` path in v0.124.0 by reusing the same credential object and comparing strings. That server-side path is present in every release through v0.150.0. The outbound `HTTPClient` path (used by Azure exporters) is unaffected.

### Details

Vulnerable code — `extension/azureauthextension/extension.go:208–235`:

```go
func (a *authenticator) Authenticate(ctx context.Context, headers map[string][]string) (context.Context, error) {
    auth, err := getHeaderValue("Authorization", headers)
    if err != nil { return ctx, err }
    host, err := getHeaderValue("Host", headers)
    if err != nil { return ctx, err }

    authFormat := strings.Split(auth, " ")
    if len(authFormat) != 2 { /* ... */ }
    if authFormat[0] != "Bearer" { /* ... */ }

    token, err := a.getTokenForHost(ctx, host)   // asks the collector's own identity
    if err != nil { return ctx, err }
    if authFormat[1] != token {                  // string comparison, not JWT validation
        return ctx, errors.New("unauthorized: invalid token")
    }
    return ctx, nil
}
```

And `getTokenForHost` at `extension.go:187–206`:

```go
options := policy.TokenRequestOptions{
    Scopes: []string{
        fmt.Sprintf("https://%s/.default", host),   // client-supplied Host chooses scope
    },
}
```

Two independent problems compose here:

**1. No JWT validation.** Real Entra ID bearer validation requires verifying the JWT signature against the tenant JWKS and checking `iss`, `aud`, `exp`, `nbf`, plus an algorithm allowlist. The extension does none of this. The "expected" value is a token the server mints from its own credential, not a signature to verify. Any party that already holds a valid token for the collector's identity — a co-tenant pod that shares the managed identity, any peer authenticated with the same service principal, any component that retained an `Authorization:` header — can replay it directly.

**2. Attacker-controlled audience.** The scope used to mint the "expected" token comes from the client-supplied `Host` header: `https://<Host>/.default`. The `azcore` credential returns a consistent token per (identity, scope) pair within the cache window, so an attacker can pick any scope the SP has been issued a token for and match it by setting `Host` accordingly. This is the sharper of the two flaws: it means a token leaked from an unrelated Azure integration — ARM, Graph, Key Vault, a different Storage account — authenticates to the collector.

The correct primitive is a real JWT validator — e.g. `github.com/coreos/go-oidc/v3` pointed at the tenant's discovery endpoint, with audience and issuer pinned *server-side from configuration*, never derived from request headers.

### Proof of concept

Both variants assume a collector running with `azureauthextension` v0.124.0–v0.150.0, configured with any credential mode and referenced from a receiver's `auth:` block:

```yaml
extensions:
  azure_auth:
    managed_identity:
      client_id: ${CLIENT_ID}

receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
        auth:
          authenticator: azure_auth

service:
  extensions: [azure_auth]
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [debug]
```

#### Variant A — Replay (same scope)

The attacker controls a workload that shares the collector's managed identity (common in AKS when multiple pods bind the same UAMI). Both workloads query IMDS for `https://management.azure.com/.default` and receive the same cached token. The attacker replays:

```
POST /v1/traces HTTP/1.1
Host: management.azure.com
Authorization: Bearer eyJ...            # token minted for management.azure.com
Content-Type: application/json

{"resourceSpans":[...]}
```

`Authenticate` calls `getTokenForHost(ctx, "management.azure.com")`, receives the identical cached token, and the string comparison passes.

#### Variant B — Scope confusion (the stronger case)

The attacker holds a token for the SP issued for a *different* Azure resource — say Key Vault, obtained from an entirely unrelated integration. The collector was never intended to accept Key Vault tokens. The attacker sets `Host` to match:

```
POST /v1/traces HTTP/1.1
Host: vault.azure.net
Authorization: Bearer eyJ...            # token minted for vault.azure.net
Content-Type: application/json

{"resourceSpans":[...]}
```

`Authenticate` calls `getTokenForHost(ctx, "vault.azure.net")`. The collector's credential mints (or returns cached) a token for `https://vault.azure.net/.default` — the same token the attacker holds, because both come from the same SP issued for the same scope by the same IdP. Comparison passes. The collector accepts telemetry gated on "proof of identity to Key Vault."

In a correct implementation, the JWT's `aud` would be pinned server-side to a value unrelated to `Host`, and Variant B would fail regardless of what the attacker put in the `Host` header.

A small Go reproducer can be built around the extension's own test harness: the existing `TestAuthenticate` in `extension_test.go` is effectively a demonstration of the broken behavior — it passes when the client-supplied token equals the server-side token for the given `Host`, which is exactly what an attacker arranges.

### Impact

**Vulnerability class:** Improper Authentication (CWE-287), with contributing CWE-347 (Improper Verification of Cryptographic Signature — no JWT validation), CWE-294 (Authentication Bypass by Capture-replay — tokens replayable for full TTL), and CWE-290 (Authentication Bypass by Spoofing — client `Host` header chooses the expected scope).

**Threat model / precondition.** The attacker needs to already hold (or be able to obtain) a valid Azure access token issued to the collector's SP for any scope. In practice this is satisfied by: (a) controlling another workload that binds the same managed identity, (b) compromising any peer authenticated with the same SP, or (c) observing an `Authorization:` header from any prior legitimate request for the SP. This is what drives the 8.1 score — the precondition is non-trivial but is routine in multi-workload Azure environments.

**Who is impacted.** Any operator of `opentelemetry-collector-contrib` v0.124.0 through v0.150.0 who configured `azureauthextension` on a receiver's `auth:` block. This applies to both HTTP and gRPC receivers — gRPC receivers surface `:authority` as `Host` through the collector's header handling, so the same exploit path applies there.

**Deployments most at risk:**
- Multi-workload Azure environments where the collector shares a managed identity with other workloads (any such workload can authenticate as an arbitrary telemetry source).
- Deployments that forward `Authorization:` headers through proxies, service meshes, or logging pipelines (one leaked token is enough, and persists for the token TTL — typically several hours for MI tokens, not the 60-minute user-token window).
- Multi-tenant environments where different customers' telemetry converges at a collector protected by this extension.

**Consequences.** Unauthenticated (from the collector's perspective) ingest of arbitrary traces, metrics, and logs. Downstream effects depend on the collector's exporters and include telemetry-backend poisoning, log injection (masking real attacker activity in SIEMs), metric manipulation to trigger or suppress alerts, cost-amplification against pay-per-datapoint backends, and adversarial traces that corrupt service-graph and incident-triage signals.

**Not impacted.** The extension's outbound `extensionauth.HTTPClient` path, used by Azure exporters, is unaffected. Operators who use `azureauthextension` only on exporters can continue doing so.

### Mitigation

Until a patched release is available, remove `azure_auth` from any receiver `auth:` blocks. For genuine Entra ID JWT validation on OTLP receivers, use `oidcauthextension` pointed at the tenant discovery URL, with audience pinned from configuration:

```yaml
extensions:
  oidc:
    issuer_url: https://login.microsoftonline.com/<tenant-id>/v2.0
    audience: <expected-api-audience>
```

### Resources

- PR introducing the vulnerable server-side path: [#39178](https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/39178)
- Affected versions: v0.124.0 – v0.150.0

Assisted-by: Opus 4.7

## References
- https://github.com/open-telemetry/opentelemetry-collector-contrib/security/advisories/GHSA-pjv4-3c63-699f
- https://nvd.nist.gov/vuln/detail/CVE-2026-42602
- https://github.com/open-telemetry/opentelemetry-collector-contrib
