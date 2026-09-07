# [H] Dex: Token-exchange endpoint is missing AllowedConnectors enforcement

## Summary
Severity: High
Advisory: GHSA-7qjx-gp9h-65qj
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-09
Source: https://github.com/advisories/GHSA-7qjx-gp9h-65qj
Type: github-advisory

## Affected
- Go: `github.com/dexidp/dex` — affected >=0 <0.0.0-20260303131938-204dbb2e3ff7

## Details
## Summary

`server/handlers.go::handleTokenExchange` (lines 1804-1893) does not call `isConnectorAllowed(client.AllowedConnectors, connID)` before issuing tokens, while sibling handlers do. This is a per-client connector ACL gap on the token-exchange endpoint; the redirect-flow paths enforce the same field correctly.

## Affected code path

`handleTokenExchange` reads `connector_id` from the request body at `server/handlers.go:1822`. Validators called between read and token issuance:

- `s.getConnector(ctx, connID)` at line 1836 - confirms connector exists
- `GrantTypeAllowed(conn.GrantTypes, grantTypeTokenExchange)` at line 1842 - confirms connector permits this grant
- **(missing)** `isConnectorAllowed(client.AllowedConnectors, connID)` - never called

Tokens are issued at lines 1887 / 1889, bound to `client.ID` carrying claims derived from `connID`.

Sibling handlers DO enforce the check:

- `server/handlers.go::handleConnectorLogin:377` - calls `isConnectorAllowed`, returns HTTP 403 "Connector not allowed for this client." (line 380).
- `server/oauth2.go::parseAuthorizationRequest:535` - same enforcement for the authorization-code flow.

The doc-string at `storage/storage.go:192-194` reads:

> *AllowedConnectors is a list of connector IDs that the client is allowed to use for authentication. If empty, all connectors are allowed.*

The phrasing is unconditional - a permission ACL, not a UX filter.

## Impact (concrete scenario)

- Connector `corp-okta` - high-trust, gates production access
- Connector `dev-google` - low-trust, internal Gmail
- Client `dev-app` configured with `allowedConnectors: ["dev-google"]` (admin intent: dev-app only sees dev-google identities)
- `dev-app`s client secret leaks (CI artifact, env file, breached service-account secret store)

Without the bug, the leaked secret would only allow the attacker to mint tokens via `dev-google` - blast radius bounded by what any dev-google user can already do.

With the bug, an attacker holding their own legitimate `corp-okta` ID token sends:

```
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:token-exchange
&client_id=dev-app
&client_secret=<leaked>
&connector_id=corp-okta
&subject_token=<attackers own corp-okta id token>
&subject_token_type=urn:ietf:params:oauth:token-type:id_token
&scope=openid+groups
```

Dex returns an ID token signed by Dex, `aud=dev-app`, carrying the attackers `corp-okta` groups. Downstream services trusting tokens issued for `dev-app` see the attacker as a `corp-okta` user - a combination the admins policy explicitly forbade.

## Severity (self-assessed)

CVSS 3.1 vector: `AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N` -> **8.7 HIGH**.

The `PR:H` precondition is a real reduction (requires leaked confidential client_secret PLUS attacker holding a `subject_token` from a forbidden connector that has token-exchange enabled). Defer to your scoring - HIGH and MEDIUM are both defensible.

## Affected version

`master` only - **not yet in any released tag**. Latest release `v2.45.1` (2026-03-03) predates PR #4610 (commit `f80a89d`, 2026-03-11) which introduced `AllowedConnectors`. Production deployments on stable releases are NOT affected; deployments pulling from master / nightly images are. A fix can be merged ahead of the next release without an embargo for past versions.

## Precedent / lineage

- PR #4610 (commit `f80a89d`, 2026-03-11) - added the `AllowedConnectors` field, `isConnectorAllowed`, `filterConnectors`, and the redirect-flow check sites (`handleConnectorLogin:377`, `parseAuthorizationRequest:535`). Did not modify `handleTokenExchange`.
- PR #4619 (commit `7777773`, 2026-03-11, same author, one day earlier) - added `GrantTypeAllowed(conn.GrantTypes, grantTypeTokenExchange)` to `handleTokenExchange`. Added a connector-side grant-type gate but did not add the symmetric client-side connector ACL.

## Suggested fix

Insert `isConnectorAllowed(client.AllowedConnectors, connID)` between the existing `getConnector` / `GrantTypeAllowed` checks and the connector cast at line 1847, returning HTTP 403 via the token-endpoint error helper. Mirror the existing patterns at `handlers.go:377-380` and `oauth2.go:535`. One-block addition.

## Verification methodology

Two-stage verification per IRIS / XBOW pattern (LLM-assisted research with non-LLM verifier as last stage):

1. **Code-mechanics** - independent cold-read of `server/handlers.go`, `server/oauth2.go`, `storage/storage.go` confirmed the missing check at `handleTokenExchange` and the present checks at the two siblings; cross-checked diffs of PR #4610 (`f80a89d`) and PR #4619 (`7777773`).
2. **External grounding** - cross-checked `docs/configuration/customization`, `docs/guides/token-exchange/`, RFC 8693 (which defers per-client policy to implementations), `.github/SECURITY.md`, GHSA dashboard, huntr.com, and existing issues including #3546 (different mechanism: connector-level disable list, orthogonal to this finding). No prior public report of this gap was found.

`semgrep` (`p/golang` + `p/security-audit`) on `server/` returned no ERROR-severity findings - the static tool cannot detect missing-validator gaps; evidence rests on file:line grep + sibling-handler comparison above.

## Reporter

Matteo Panzeri (GitHub: @matte1782, contact: matteo1782@gmail.com). Please credit as **Matteo Panzeri** if a CVE is requested.

## References
- https://github.com/dexidp/dex/security/advisories/GHSA-7qjx-gp9h-65qj
- https://github.com/dexidp/dex/commit/204dbb2e3ff7692af3b7ca4362b1ee46fb43c227
- https://github.com/dexidp/dex
