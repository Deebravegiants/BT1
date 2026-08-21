# Q1287: Error propagation in orb_relay_announce_orb_id downgrades a hard failure (plans/mod.rs)

## Question
Can an unprivileged attacker force an error inside `orb_relay_announce_orb_id` in [src/plans/mod.rs](src/plans/mod.rs) that is logged and swallowed rather than propagated, so the signup continues without the guarantee that failed step provided?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `orb_relay_announce_orb_id` (function)
- Entrypoint: Inducing the failure through normal capture/scan conditions
- Attacker controls: scene, distance, or payload conditions that reliably trigger the error branch
- Exploit idea: Trace each `Err`/`warn!` site in `orb_relay_announce_orb_id` for continuation instead of abort.
- Invariant to test: Security-relevant step failures abort the signup; only cosmetic failures may be logged and ignored.
- Expected Immunefi impact: Signup completed with a silently skipped security step
- Fast validation: Fault-injection test forcing each error site in `orb_relay_announce_orb_id` and asserting abort.
