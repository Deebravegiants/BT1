# Q4628: get-egroup via borrow: mint shares whose backing was never received

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the order of accrual versus price resolution inside the let reach `get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) in a state where it mint shares whose backing was never received? Given that it resolves the efficiency group for a mask and is unwrapped with `try!` on every health path, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the order of accrual versus price resolution inside the let varied, and assert that the value `get-egroup` returns is identical in both runs; a divergence confirms the finding.
