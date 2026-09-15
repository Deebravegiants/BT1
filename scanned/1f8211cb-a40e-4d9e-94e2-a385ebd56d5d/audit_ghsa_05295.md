# [M] SurrealDB: SSRF via JWKS URL — Redirect Following in JWT Key Fetch

## Summary
Severity: Medium
Advisory: GHSA-h5rg-8p7f-47g2
CWE: CWE-918
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-h5rg-8p7f-47g2
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.5

## Details
SurrealDB fetches the JWKS document for a JWT or record access method using a bare `reqwest` client that follows HTTP redirects by default. The network capability check in `core/src/iam/jwks.rs` (`check_capabilities_url`) is applied only to the originally configured URL; redirect targets are not re-validated. An `--allow-net`-permitted JWKS host that returns a `3xx Location` can therefore redirect the request to an address the allowlist was meant to block, resulting in a server-side request forgery (SSRF). The protected `HttpClient` used by `http::*` functions re-checks every redirect hop and was hardened in 3.1.0, but the JWKS fetcher uses its own client and was not covered.

### Impact

What an attacker **can** do:

- With the **Owner** role at database level or above (the minimum required to run `DEFINE ACCESS ... TYPE JWT URL` or `TYPE RECORD ... WITH JWT URL`), point an access method at an allowlisted host they control and redirect the server's GET to an otherwise-blocked target — cloud metadata, loopback, internal services — bypassing `--allow-net`/`--deny-net`.
- Infer the existence and liveness of internal hosts and ports from response-timing differences (bounded by the 1-second fetch timeout).

What it **can't** do:

- Read the response: the fetch is blind — the body is only parsed as a JWKS, and a non-JWKS response surfaces as an opaque `InvalidAuth` error. Nothing is returned to the caller.
- Modify data or affect availability (a single GET request).

### Patches

The JWKS fetcher now applies a redirect policy that re-validates every redirect target against the configured network capabilities (mirroring `check_capabilities_url`) and caps redirects at `max_http_redirects`.

- Versions prior to 3.1.5 are vulnerable.

### Workarounds

- Restrict the Owner role to trusted operators.
- Enforce egress filtering at the network layer (block link-local `169.254.0.0/16` and internal ranges) so redirect targets are unreachable regardless of in-process checks.
- Configure access methods to use only trusted JWKS hosts that do not redirect, or use locally defined keys instead of a remote JWKS.

### References

- [SurrealDB Documentation — Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities)
- [SurrealQL Documentation — DEFINE ACCESS](https://surrealdb.com/docs/surrealql/statements/define/access)
- `fix(iam): prevent SSRF in JWKS fetch by re-validating redirect targets`

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-h5rg-8p7f-47g2
- https://github.com/surrealdb/surrealdb
