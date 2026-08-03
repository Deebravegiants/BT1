# Q0554: remove_other_vote replay can duplicate a governance-side effect

## Question
Can an unprivileged attacker repeat `remove_other_vote` and make one logical governance action apply twice before `delegations` or terminal status closes it?

## Target
- File/function: substrate/frame/conviction-voting/src/lib.rs::remove_other_vote
- Entrypoint: signed extrinsic `remove_other_vote`
- Attacker controls: IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts
- Exploit idea: Probe stale indexes, status flags, and public cleanup paths that may remain callable after first settlement.
- Invariant to test: Public governance actions must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Replay identical and near-identical calls at every lifecycle stage and verify no second vote, payout, refund, or proposal mutation occurs.
