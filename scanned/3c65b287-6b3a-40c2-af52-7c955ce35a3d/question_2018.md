# Q2018: Attacker-controlled value interpolated into a request URL by request_tiered_package (backend/presigned_url.rs)

## Question
Can an unprivileged attacker put path separators, `..`, or query/fragment delimiters into an identity field that `request_tiered_package` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) interpolates into a backend URL, redirecting the request to a different resource or another user's record?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `request_tiered_package` (function)
- Entrypoint: Identity fields originating in the scanned QR payload
- Attacker controls: the exact string of the identity/session field
- Exploit idea: Check `request_tiered_package` for percent-encoding or an allowlist on components joined into the URL.
- Invariant to test: Every attacker-influenced URL component is strictly validated and percent-encoded.
- Expected Immunefi impact: Cross-user record access or request redirection from a scanned code
- Fast validation: Unit-test `request_tiered_package` with traversal/delimiter-laden components asserting encoding or rejection.
