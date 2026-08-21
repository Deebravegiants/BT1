# Q3047: Attacker-controlled value interpolated into a request URL by compute_hyrax_commitment (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker put path separators, `..`, or query/fragment delimiters into an identity field that `compute_hyrax_commitment` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) interpolates into a backend URL, redirecting the request to a different resource or another user's record?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `compute_hyrax_commitment` (function)
- Entrypoint: Identity fields originating in the scanned QR payload
- Attacker controls: the exact string of the identity/session field
- Exploit idea: Check `compute_hyrax_commitment` for percent-encoding or an allowlist on components joined into the URL.
- Invariant to test: Every attacker-influenced URL component is strictly validated and percent-encoded.
- Expected Immunefi impact: Cross-user record access or request redirection from a scanned code
- Fast validation: Unit-test `compute_hyrax_commitment` with traversal/delimiter-laden components asserting encoding or rejection.
