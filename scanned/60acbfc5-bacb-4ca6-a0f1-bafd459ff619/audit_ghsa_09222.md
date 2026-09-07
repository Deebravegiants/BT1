# [M] nuts-node has JWT type confusion in v1 access token introspection that allows VP replay as access token

## Summary
Severity: Medium
Advisory: GHSA-9hmg-827w-9rhj
CVE: CVE-2026-41164
CWE: CWE-345
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-9hmg-827w-9rhj
Type: github-advisory

## Affected
- Go: `github.com/nuts-foundation/nuts-node` — affected >=0

## Details
## Summary

The v1 access token introspection endpoint (`/auth/v1/introspect_access_token`) accepts any JWT signed by a key present on the node, without validating the JWT type, issuer-to-key binding, or required claims. This allows a Verifiable Presentation (VP) JWT to be replayed as an access token and receive an `active: true` introspection response.

## Background

In the v1 auth flow ([Nuts RFC003](https://nuts-foundation.gitbook.io/v1/rfc/rfc003-oauth2-authorization)), access tokens are JWTs signed by the authorizer's key with:
- `iss` = authorizer organization DID
- `sub` = requester organization DID
- `service` = purpose of use (e.g. `"eOverdracht"`)
- `typ` header = `"JWT"` (default, not explicitly set)

Verifiable Presentations are also JWTs with `typ: "JWT"` (per W3C VC Data Model 1.1). The W3C VC Data Model 2.0 changed this to `vp+jwt` specifically to prevent this class of confusion attack (See [Securing Verifiable Credentials using JOSE and COSE 3.1.1](https://www.w3.org/TR/vc-jose-cose/#securing-with-jose)).

## Vulnerability details

The introspection endpoint performs only standard JWT checks. It does not perform the following Nuts-specific access token checks:

1. **Validate the `typ` header**: both ATs and VPs use `"JWT"`
2. **Bind `iss` to the signing key**: it doesn't verify that the `iss` claim matches the DID extracted from the `kid`
3. **Validate required claims**: `service` can be empty; `vp` claim is silently ignored by `FromMap()` which uses lenient JSON unmarshaling

## Attack scenario

**Prerequisites:** Attacker (Org B) has received a VP JWT from the victim (Org A) during a normal access token request flow.

1. Org A creates a VP JWT signed with Org A's key and sends it to Org B (normal protocol flow) to request an access token
2. Org B presents this VP JWT to Org A's resource server as a bearer access token
3. Resource server calls Org A's v1 introspection endpoint
4. Introspection checks `privateKeyStore.Exists(kid)`, which passes, because Org A's key is on Org A's node
5. JSON unmarshaling is lenient; the `vp` claim is silently ignored
6. Returns `active: true` with `service: ""`, `iss: ""`, `sub: <Org A's DID>`

## Mitigating factors

- **`service` is empty**: resource servers that strictly require a non-empty `service` field may reject the request at the application level
- **`iss` is empty**: VP JWTs don't set `iss`, so resource servers checking this field would see an empty value
- **Short-lived VPs**: VPs typically expire within minutes, narrowing the attack window
- **v1 is legacy**: the v2 flow uses opaque access tokens and is not affected

## Severity rationale

While the introspection endpoint incorrectly returns `active: true` for a replayed VP, we consider this not practically exploitable in the current deployment landscape. Resource servers require valid `service`, `iss` and `aud` values to route requests to the correct databases. A replayed VP returns empty `service`, empty `iss`, and wrong `sub` (Org A instead of B), making it unusable for meaningful access. The attack also requires the victim to first present a VP to the attacker through a legitimate protocol flow, and VPs are short-lived.

The severity reflects that the protection against exploitation is accidental (resource servers need `service` for routing, not for security) and we cannot guarantee how all resource server implementations handle the `active: true` response with missing fields.

## The fix

Affected versions: all v5.x releases prior to v5.4.31, and all v6.x releases prior to v6.2.3. From v5.4.31 and v6.2.3 onward, the following checks have been added to `IntrospectAccessToken`:

1. **`iss`-to-`kid` binding**: extract the DID from the `kid` header and verify it matches the `iss` claim
2. **Required claims validation**: reject tokens where `service` is empty
3. **`typ` header validation**: requires access tokens to be of `typ: "at+jwt"`

Additionally, the access token creation code has been updated to use `typ: "at+jwt"` per RFC 9068.

## Patch

Patches are available at https://github.com/nuts-foundation/nuts-node/releases/tag/v5.4.31 and https://github.com/nuts-foundation/nuts-node/releases/tag/v6.2.3.

## Workaround

If users are unable to update their nuts-node, resource servers can mitigate this risk by explicitly validating the introspection response: reject responses where `service` is empty, where `iss` is empty or does not match the expected authorizer DID, or where `sub` does not match the expected requester DID (Org B instead of A).

## References
- https://github.com/nuts-foundation/nuts-node/security/advisories/GHSA-9hmg-827w-9rhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-41164
- https://github.com/nuts-foundation/nuts-node
- https://github.com/nuts-foundation/nuts-node/releases/tag/v5.4.31
- https://github.com/nuts-foundation/nuts-node/releases/tag/v6.2.3
