# Q1370: submit can reuse an index or hash too early

## Question
Can an unprivileged attacker use `submit` so a proposal index, referendum index, bounty ID, reason hash, or spend record is treated as reusable before every old reference is dead?

## Target
- File/function: substrate/frame/referenda/src/lib.rs::submit
- Entrypoint: signed extrinsic `submit`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Probe cancellation, closure, and metadata-clearing edges around index lifecycle.
- Invariant to test: Closed governance identifiers must not collide with still-live deposits, metadata, or claim paths.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Create and close one object, then immediately reuse adjacent identifiers or equivalent hashes and test every old public follow-up path.
