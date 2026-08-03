# Q1373: check_status can reuse an index or hash too early

## Question
Can an unprivileged attacker use `check_status` so a proposal index, referendum index, bounty ID, reason hash, or spend record is treated as reusable before every old reference is dead?

## Target
- File/function: substrate/frame/treasury/src/lib.rs::check_status
- Entrypoint: signed extrinsic `check_status`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe cancellation, closure, and metadata-clearing edges around index lifecycle.
- Invariant to test: Closed governance identifiers must not collide with still-live deposits, metadata, or claim paths.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Create and close one object, then immediately reuse adjacent identifiers or equivalent hashes and test every old public follow-up path.
