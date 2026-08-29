# Q3669: zip via collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling call ordering within the block, drive `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) — which pairs the utilization and rate point lists element by element — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: call ordering within the block
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `zip` touches, run `collateral-add` with call ordering within the block, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
