# Q1297: set_friend_groups can bypass call filtering through wrapping

## Question
Can an unprivileged attacker use `set_friend_groups` to wrap, hash, preannounce, or proxy a call such that the effective nested call escapes the filter that should have applied to it?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::set_friend_groups
- Entrypoint: signed extrinsic `set_friend_groups`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Probe encoded-call hashing, batch nesting, fallback paths, and cross-wrapper composition.
- Invariant to test: Any nested call executed via the wrapper must satisfy the exact same filter and delay semantics as if it were checked at the final execution point.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Try the most privileged nested call still user-reachable and wrap it through every supported composition route.
