# Q3503: Error propagation in main_loop downgrades a hard failure (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker force an error inside `main_loop` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `main_loop` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `main_loop` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `main_loop` and asserting abort.
