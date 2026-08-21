# Q1967: Attacker-controlled value interpolated into a request URL by client_with_timeouts (backend/mod.rs)

## Question
Can an unprivileged attacker put path separators, `..`, or query/fragment delimiters into an identity field that `client_with_timeouts` in [src/backend/mod.rs](src/backend/mod.rs) interpolates into a backend URL, redirecting the request to a different resource or another user's record?

## Target
- File/function: [src/backend/mod.rs](src/backend/mod.rs) -> `client_with_timeouts` (function)
- Entrypoint: Identity fields originating in the scanned QR payload
- Attacker controls: the exact string of the identity/session field
- Exploit idea: Check `client_with_timeouts` for percent-encoding or an allowlist on components joined into the URL.
- Invariant to test: Every attacker-influenced URL component is strictly validated and percent-encoded.
- Expected Immunefi impact: Cross-user record access or request redirection from a scanned code
- Fast validation: Unit-test `client_with_timeouts` with traversal/delimiter-laden components asserting encoding or rejection.
