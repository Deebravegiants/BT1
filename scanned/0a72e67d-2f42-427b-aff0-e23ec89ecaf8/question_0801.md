# Q0801: Attacker-controlled value interpolated into a request URL by DATA_BACKEND_URL (backend/endpoints.rs)

## Question
Can an unprivileged attacker put path separators, `..`, or query/fragment delimiters into an identity field that `DATA_BACKEND_URL` in [src/backend/endpoints.rs](src/backend/endpoints.rs) interpolates into a backend URL, redirecting the request to a different resource or another user's record?

## Target
- File/function: [src/backend/endpoints.rs](src/backend/endpoints.rs) -> `DATA_BACKEND_URL` (item)
- Entrypoint: Identity fields originating in the scanned QR payload
- Attacker controls: the exact string of the identity/session field
- Exploit idea: Check `DATA_BACKEND_URL` for percent-encoding or an allowlist on components joined into the URL.
- Invariant to test: Every attacker-influenced URL component is strictly validated and percent-encoded.
- Expected Immunefi impact: Cross-user record access or request redirection from a scanned code
- Fast validation: Unit-test `DATA_BACKEND_URL` with traversal/delimiter-laden components asserting encoding or rejection.
