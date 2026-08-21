# Q1991: Attacker-controlled value interpolated into a request URL by do_request (backend/user_status.rs)

## Question
Can an unprivileged attacker put path separators, `..`, or query/fragment delimiters into an identity field that `do_request` in [src/backend/user_status.rs](src/backend/user_status.rs) interpolates into a backend URL, redirecting the request to a different resource or another user's record?

## Target
- File/function: [src/backend/user_status.rs](src/backend/user_status.rs) -> `do_request` (function)
- Entrypoint: Identity fields originating in the scanned QR payload
- Attacker controls: the exact string of the identity/session field
- Exploit idea: Check `do_request` for percent-encoding or an allowlist on components joined into the URL.
- Invariant to test: Every attacker-influenced URL component is strictly validated and percent-encoded.
- Expected Immunefi impact: Cross-user record access or request redirection from a scanned code
- Fast validation: Unit-test `do_request` with traversal/delimiter-laden components asserting encoding or rejection.
