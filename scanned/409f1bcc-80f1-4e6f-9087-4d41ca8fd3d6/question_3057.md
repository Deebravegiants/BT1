# Q3057: mask-shift-combine via collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling call ordering within the block, drive `mask-shift-combine` (mainnet/contracts/market/v0-4-market.clar:422) — which folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:422` -> `mask-shift-combine`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `mask-shift-combine` folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `mask-shift-combine` touches, run `collateral-add` with call ordering within the block, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
