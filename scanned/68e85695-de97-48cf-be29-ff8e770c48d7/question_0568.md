# Q0568: buy_ticket replay can duplicate a governance-side effect

## Question
Can an unprivileged attacker repeat `buy_ticket` and make one logical governance action apply twice before `Calls` or terminal status closes it?

## Target
- File/function: substrate/frame/lottery/src/lib.rs::buy_ticket
- Entrypoint: signed extrinsic `buy_ticket`
- Attacker controls: nested call payloads
- Exploit idea: Probe stale indexes, status flags, and public cleanup paths that may remain callable after first settlement.
- Invariant to test: Public governance actions must be idempotent under duplicates and replays.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Replay identical and near-identical calls at every lifecycle stage and verify no second vote, payout, refund, or proposal mutation occurs.
