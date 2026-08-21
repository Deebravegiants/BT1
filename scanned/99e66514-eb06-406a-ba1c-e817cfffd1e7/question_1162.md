# Q1162: Error propagation in wait_for_connect_response downgrades a hard failure (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker force an error inside `wait_for_connect_response` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `wait_for_connect_response` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `wait_for_connect_response` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `wait_for_connect_response` and asserting abort.
