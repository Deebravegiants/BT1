# Q0572: set_metadata replay can duplicate a governance-side effect

## Question
Can an unprivileged attacker repeat `set_metadata` and make one logical governance action apply twice before `submission deposit` or terminal status closes it?

## Target
- File/function: substrate/frame/referenda/src/lib.rs::set_metadata
- Entrypoint: signed extrinsic `set_metadata`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Probe stale indexes, status flags, and public cleanup paths that may remain callable after first settlement.
- Invariant to test: Public governance actions must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Replay identical and near-identical calls at every lifecycle stage and verify no second vote, payout, refund, or proposal mutation occurs.
