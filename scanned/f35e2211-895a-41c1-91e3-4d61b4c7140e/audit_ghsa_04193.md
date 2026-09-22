# [M] http4k: `ServerFilters.DigestAuth` / `DigestAuthProvider` defaulted to an always-true nonce verifier, disabling replay protection in default deployments

## Summary
Severity: Medium
Advisory: GHSA-c7jm-38gq-h67h
CWE: CWE-294
Ecosystem: Maven
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-c7jm-38gq-h67h
Type: github-advisory

## Affected
- Maven: `org.http4k:http4k-security-digest` — affected >=6.0.0.0 <6.48.0.0
- Maven: `org.http4k:http4k-security-digest` — affected >=5.0.0.0 <5.42.0.0
- Maven: `org.http4k:http4k-security-digest` — affected >=0 <4.51.0.0

## Details
### Impact

`ServerFilters.DigestAuth` and the underlying `DigestAuthProvider` both defaulted their `nonceVerifier` parameter to `{ true }` — i.e. every nonce was accepted regardless of value, age, or prior use. Any deployment using the default configuration had **no replay protection** on Digest authentication; a captured `Authorization: Digest …` response could be replayed indefinitely against the same protected resource.

The nonce-verification mechanism in Digest auth is the primary anti-replay control — without it, Digest reduces to a credential bound only to a stale nonce string.

**Who is affected:** any application using `ServerFilters.DigestAuth` or `DigestAuthProvider` with the default `nonceVerifier`. The broken default has been present since `DigestAuthProvider` was introduced (2021). Exploitation requires the attacker to first capture a valid Digest response (network observation, log access, etc.) — non-trivial in modern TLS deployments but not impossible. Anyone running Digest auth with default config should treat upgrade as urgent.

### Patches

| Line | Fixed in | Edition |
|------|----------|---------|
| v6.x (Community) | **6.48.0.0** | Community |
| v5.x (LTS) | **5.42.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) (if Digest auth is present in your v5.x line) |
| v4.x (LTS) | **4.51.0.0** | Enterprise — contact [enterprise@http4k.org](mailto:enterprise@http4k.org) (if Digest auth is present in your v4.x line) |

The fix (`[Break]`) removes the default value for `nonceVerifier` from both `ServerFilters.DigestAuth` and `DigestAuthProvider`. Callers must now supply a real verifier explicitly — the broken default cannot be silently inherited.

### Workarounds

For deployments that cannot upgrade immediately: explicitly supply a `nonceVerifier` that tracks issued nonces, enforces a TTL, and rejects re-use. Do not rely on the default.

## References
- https://github.com/http4k/http4k/security/advisories/GHSA-c7jm-38gq-h67h
- https://github.com/http4k/http4k/commit/4f904b4692
- https://github.com/http4k/http4k/commit/8a52b615b1
- https://datatracker.ietf.org/doc/html/rfc7616#section-3.4
- https://github.com/http4k/http4k
- https://github.com/http4k/http4k/releases/tag/6.48.0.0
