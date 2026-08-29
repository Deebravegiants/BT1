# Q0738: mask-shift-combine via borrow: mint shares whose backing was never received

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the order of accrual versus price resolution inside the let, can an unprivileged attacker make `mask-shift-combine` (mainnet/contracts/market/v0-4-market.clar:422) mint shares whose backing was never received? `mask-shift-combine` folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:422` -> `mask-shift-combine`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `mask-shift-combine` folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the order of accrual versus price resolution inside the let across its boundary values through `borrow` in simnet and assert `mask-shift-combine` never returns a value that breaks the invariant.
