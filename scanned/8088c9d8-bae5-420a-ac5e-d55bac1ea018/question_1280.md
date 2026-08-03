# Q1280: unnote_preimage can bypass call filtering through wrapping

## Question
Can an unprivileged attacker use `unnote_preimage` to wrap, hash, preannounce, or proxy a call such that the effective nested call escapes the filter that should have applied to it?

## Target
- File/function: substrate/frame/preimage/src/lib.rs::unnote_preimage
- Entrypoint: signed extrinsic `unnote_preimage`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe encoded-call hashing, batch nesting, fallback paths, and cross-wrapper composition.
- Invariant to test: Any nested call executed via the wrapper must satisfy the exact same filter and delay semantics as if it were checked at the final execution point.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Try the most privileged nested call still user-reachable and wrap it through every supported composition route.
