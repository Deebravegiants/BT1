# Q0275: set_metadata can desync deposits from live governance state

## Question
Can an unprivileged attacker call `set_metadata` with crafted call repetition, batching order, and surrounding state so deposits tracked alongside `PublicProps` or `DepositOf` are reserved, refunded, or slashed inconsistently with the surviving governance object?

## Target
- File/function: substrate/frame/democracy/src/lib.rs::set_metadata
- Entrypoint: signed extrinsic `set_metadata`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Target lifecycle edges where a proposal, vote, bounty, spend, or tip changes state across multiple ledgers.
- Invariant to test: Deposits and the governance objects they back must be one-to-one across creation, settlement, and cleanup.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Track reserved balances through creation, execution, cancellation, closure, and refund and assert exact one-time settlement.
