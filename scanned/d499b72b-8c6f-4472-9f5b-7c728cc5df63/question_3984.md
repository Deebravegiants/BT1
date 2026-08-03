# Q3984: approve_transfer can consume stale delegated authority twice

## Question
Can an unprivileged attacker use `approve_transfer` to spend, approve, or clear delegated authority in a way that lets the same approval or third-party entitlement be used twice?

## Target
- File/function: substrate/frame/assets/src/lib.rs::approve_transfer
- Entrypoint: signed extrinsic `approve_transfer`
- Attacker controls: amounts, fees, or prices, IDs, hashes, nonces, or location fields, beneficiary, delegate, or target accounts
- Exploit idea: Target stale approval snapshots, reordered approval updates, or failure paths that refund deposits without clearing effective authorization.
- Invariant to test: Delegated authority must be single-use exactly to the extent recorded in storage and may not survive cancellation or partial execution.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Replay delegated flows across the same approval with slight parameter changes and assert residual allowance decreases exactly once.
