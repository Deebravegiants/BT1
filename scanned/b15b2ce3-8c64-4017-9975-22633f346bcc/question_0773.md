# Q0773: Attacker-controlled value interpolated into a request URL by SaveFusionRnFiInput (agents/image_notary.rs)

## Question
Can an unprivileged attacker put path separators, `..`, or query/fragment delimiters into an identity field that `SaveFusionRnFiInput` in [src/agents/image_notary.rs](src/agents/image_notary.rs) interpolates into a backend URL, redirecting the request to a different resource or another user's record?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `SaveFusionRnFiInput` (type)
- Entrypoint: Identity fields originating in the scanned QR payload
- Attacker controls: the exact string of the identity/session field
- Exploit idea: Check `SaveFusionRnFiInput` for percent-encoding or an allowlist on components joined into the URL.
- Invariant to test: Every attacker-influenced URL component is strictly validated and percent-encoded.
- Expected Immunefi impact: Cross-user record access or request redirection from a scanned code
- Fast validation: Unit-test `SaveFusionRnFiInput` with traversal/delimiter-laden components asserting encoding or rejection.
