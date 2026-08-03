# Q0286: retract_tip can desync deposits from live governance state

## Question
Can an unprivileged attacker call `retract_tip` with crafted IDs, hashes, nonces, or location fields so deposits tracked alongside `Tips` or `Reasons` are reserved, refunded, or slashed inconsistently with the surviving governance object?

## Target
- File/function: substrate/frame/tips/src/lib.rs::retract_tip
- Entrypoint: signed extrinsic `retract_tip`
- Attacker controls: IDs, hashes, nonces, or location fields
- Exploit idea: Target lifecycle edges where a proposal, vote, bounty, spend, or tip changes state across multiple ledgers.
- Invariant to test: Deposits and the governance objects they back must be one-to-one across creation, settlement, and cleanup.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Track reserved balances through creation, execution, cancellation, closure, and refund and assert exact one-time settlement.
