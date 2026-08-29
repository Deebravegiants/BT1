# Q3141: add-user-collateral via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling vault share price at the moment of the deposit leg, drive `add-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:198) — which adds to the collateral row with a graceful u0 default — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:198` -> `add-user-collateral`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `add-user-collateral` adds to the collateral row with a graceful u0 default. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `add-user-collateral` touches, run `supply-collateral-add` with vault share price at the moment of the deposit leg, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
