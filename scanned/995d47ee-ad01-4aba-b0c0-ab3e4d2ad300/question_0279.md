# Q0279: buy_ticket can desync deposits from live governance state

## Question
Can an unprivileged attacker call `buy_ticket` with crafted nested call payloads so deposits tracked alongside `Lottery` or `Tickets` are reserved, refunded, or slashed inconsistently with the surviving governance object?

## Target
- File/function: substrate/frame/lottery/src/lib.rs::buy_ticket
- Entrypoint: signed extrinsic `buy_ticket`
- Attacker controls: nested call payloads
- Exploit idea: Target lifecycle edges where a proposal, vote, bounty, spend, or tip changes state across multiple ledgers.
- Invariant to test: Deposits and the governance objects they back must be one-to-one across creation, settlement, and cleanup.
- Expected Immunefi impact: Unauthorized treasury, bounty, or governance outcome with financial impact
- Fast validation: Track reserved balances through creation, execution, cancellation, closure, and refund and assert exact one-time settlement.
